---
id: meta-anyres
section: meta
order: 26
level: A
title: Meta：任意分辨率切块（AnyRes / 动态 tile）和上下文预算
quick: >-
  高分辨率不是把整图 squish 进固定 ViT，是按长宽比切成至多 $K$ 块 tile（3.2 公开默认 $K=4$）再编码。LLaVA
  AnyRes 把块 token 拼进 LM 窗；Llama 3.2 块走 encoder，LM 自注意力几乎不涨，涨的是视觉 $N$ 和
  cross-attn。预算要按融合方式算，不要只报「支持任意分辨率」。
tags:
  - Meta
  - Llama
  - Vision
  - AnyRes
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: LLaVA-NeXT — Improved reasoning, OCR, and world knowledge
    url: https://llava-vl.github.io/blog/2024-01-30-llava-next/
    type: primary
  - title: Mllama — Hugging Face Transformers
    url: https://huggingface.co/docs/transformers/main/en/model_doc/mllama
    type: primary
  - title: Llama Guard 3 Vision
    url: https://arxiv.org/abs/2411.10414
    type: secondary
  - title: Llama 3.2 vision blog
    url: https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/
    type: secondary
---

文档 VQA、截图、地图会问「分辨率不够怎么办」。公开两条线要分开讲：LLaVA-NeXT 把 **AnyRes** 写成网格切块 + 一张全局缩略图，视觉 token **进 LM 序列**；Llama 3.2 / Mllama 是 **长宽比感知的 tile**，默认最多 $4$ 块，视觉表示进 cross-attn，见 `meta-llama-vision`。面试说「任意分辨率」而不说 $K$、不说吃的是哪一段计算，等于没答。Gemini 侧可变分辨率 / packing 见 `google-gemini-mm`。

## 切块在选什么

固定 $S\times S$ 的 ViT 不能直接吃 4k 截图。做法是：保持长宽比，把图画到 $r\times c$ 块 tile 的画布上，$r\cdot c\le K$，选浪费像素最少的网格。Mllama 在 $K=4$ 时公开候选大约是 $1\times1$、$1\times2$、$1\times3$、$1\times4$、$2\times1$、$2\times2$、$3\times1$、$4\times1$。竖长海报走 $4\times1$，宽屏截图走 $1\times4$，接近方形走 $2\times2$。块不够的位置用 aspect-ratio mask 盖掉，不要让 pad 块进注意力。

```python
def pick_tiles(h, w, tile=560, max_tiles=4):
    cands = [(r, c) for r in range(1, max_tiles + 1)
             for c in range(1, max_tiles + 1) if r * c <= max_tiles]
    def waste(rc):
        r, c = rc
        scale = min(r * tile / h, c * tile / w)
        return r * c * tile * tile - (h * scale) * (w * scale)
    return min(cands, key=waste)
```

Meta Guard 3 Vision 论文写图像会 rescale 成 **$4$ 块 $560\times 560$**。Patch $14$ 时单块约 $(560/14)^2=1600$ 个 patch。这是公开实现细节，不是「一张图一个向量」。LLaVA-NeXT 的 AnyRes 网格是 $\{2\times2,\,1\times\{2,3,4\},\,\{2,3,4\}\times1\}$，并且 **额外留一张低分辨率全图**，怕切块之后丢全局。3.2 的「全局」主要在视觉塔后 $8$ 层 global encoder 里跨 tile 做自注意力，不是再往 LM 里塞一套缩略图像素 token。别把两种「全局」说成同一个算子。

## 预算：吃窗还是吃旁路

同一句「$4$ 块」在两种融合里价钱完全不同。

**拼接进 LM（LLaVA AnyRes）。** 每块 ViT 出 $P$ 个 token，再加缩略图 $P$ 个。粗算 $K=4$、$P=576$ 时约 $5\times576=2880$ 个视觉 token 进自注意力。它们占 $128\mathrm{k}$ 里的位置，和聊天记录抢 $T$，prefill FLOPs 是 $(T_{\mathrm{txt}}+T_{\mathrm{vis}})^2$。多图、高 $K$、视频帧会先把窗打满。产品上要先压分辨率、再决定切几块。

**Llama 3.2 cross-attn。** 文本序列几乎不涨（几个 image 占位符）。涨的是：视觉 encoder 按 tile 线性；cross-attn 的 $N\approx K\cdot P$；decode 每步对这 $N$ 做一次 $QK^{\top}$。$K=4$、$P=1600$ 时 $N$ 约 $6.4\mathrm{k}$，八层 cross-attn 都能看见。**$128\mathrm{k}$ 文本窗还在，但首 token 延迟和视觉 KV 显存已经按 $K$ 涨。** 把「不占上下文」说成「免费」，是错的。

Serving 账三列：encoder 时延、视觉 KV 字节、对 TPOT 的 cross-attn 增量。图不变应缓存视觉 $K/V$；用户只追加一句文本，不要重跑 ViT。Batch 里不同图 $K$ 不同，要 pad 到 `max_num_tiles` 再用 mask，否则 $2\times2$ 和 $1\times1$ 不能拼 batch。分页 KV 管的是 **文本自注意力** 的 cache，见 `sys-paged-attn`；视觉旁路要单独算，不要假定 vLLM 一开 PagedAttention 图就不占显存，见 `meta-vllm`。

错法：所有图都 pad 成正方形再缩到 $224$，字和 UI 没了。错法二：把 $K$ 开到 $6\times6$ 还不改位置编码和训练分布，推理切块训练没见过，OCR 会花。错法三：用 haystack 文本长度证明「视觉长上下文」，测的不是读图。

## 追问

- **为什么不无限切？** Encoder、$N$、延迟都线性（或更差）。公开默认 $K=4$ 是质量和成本的折中。文档密集再涨 $K$，风景图不必。
- **缩略图还要吗？** 拼接式 AnyRes 要，否则只有局部块、没有「这是一张发票」。3.2 把跨块混合放在 vision global 层；两种实现不要混着画。
- **竖图 / 横图质量差？** 往往是网格选错或 pad 没 mask。先报选了哪个 $(r,c)$，再谈模型。
- **多图对话？** Mllama 按图 pad 到 batch 内最大图数；Guard 3 Vision 公开只保证 **每条一条图**。多图安全见 `meta-mm-safety`，别默认 Guard 能吃图集。
- **和 NaViT 呢？** NaViT 是可变分辨率 pack 进同一 ViT batch。AnyRes / 3.2 tile 是推理时选离散网格。面试抓住「谁吃 LM 窗」即可。
