---
id: meta-anyres
section: meta
order: 26
level: A
title: Meta：任意分辨率切块（AnyRes / 动态 tile）和上下文预算
quick: "动态切块先按长宽比选择至多 $K$ 个 tile，保留细节又限制视觉计算，Llama 3.2 默认 $K=4$。LLaVA AnyRes 的视觉 token 占 LM 窗口，Llama 3.2 通过 cross-attn 读图，文本长度几乎不涨，但视觉 KV 与生成开销仍随 tile 数增加。"
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

任意分辨率图像通常先按长宽比切成有限数量的 tile，再编码，避免把文档小字或截图 UI 一次缩小后丢掉。接着要看融合方式：LLaVA AnyRes 把视觉 token 放进 LM 序列，Llama 3.2 / Mllama 则通过 cross-attn 读取独立视觉表示，两者的预算账不同。

固定 $S\times S$ 的 ViT 不能直接接 4k 截图，可以把图按比例放到 $r\times c$ 的 tile 画布，满足 $r\cdot c\le K$，选择浪费像素少的 $(r,c)$ 网格。Mllama 默认 $K=4$，候选约为 $1\times1$、$1\times2$、$1\times3$、$1\times4$、$2\times1$、$2\times2$、$3\times1$、$4\times1$。竖海报可选 $4\times1$，宽截图选 $1\times4$，近方形选 $2\times2$，不足的 pad tile 用 aspect-ratio mask 屏蔽。

```python
def pick_tiles(h, w, tile=560, max_tiles=4):
    cands = [
        (r, c)
        for r in range(1, max_tiles + 1)
        for c in range(1, max_tiles + 1)
        if r * c <= max_tiles
    ]

    def waste(rc):
        r, c = rc
        scale = min(r * tile / h, c * tile / w)
        return r * c * tile * tile - (h * scale) * (w * scale)

    return min(cands, key=waste)
```

Guard 3 Vision 论文写到 rescale 为 $4$ 块 $560\times 560$，patch 为 $14$ 时每块约 $(560/14)^2=1600$ 个 patch。LLaVA-NeXT AnyRes 使用 $\{2\times2,\,1\times\{2,3,4\},\,\{2,3,4\}\times1\}$ 网格，再加一张低分辨率全图保留整体语义。3.2 的跨 tile 全局信息主要由视觉塔后的 $8$ 层 global encoder self-attention 混合，不等同于额外往 LM 加缩略图 token。架构见 `meta-llama-vision`，Gemini 的可变分辨率 / packing 见 `google-gemini-mm`。

## 视觉预算算在哪里

LLaVA 拼接方式每块产生 $P$ 个 token，缩略图再加 $P$。例如 $K=4$、$P=576$，约 $5\times576=2880$ 个视觉 token 进入 LM self-attention，占用 $128\mathrm{k}$ 窗口中的 $T$，prefill FLOPs 随 $(T_{\mathrm{txt}}+T_{\mathrm{vis}})^2$ 增长。多图、视频帧、高 $K$ 都会挤占聊天历史，需要先决定分辨率与块数。

Llama 3.2 文本端只有少量 image 占位符，但视觉 encoder 按 tile 增长，cross-attn 读取的视觉长度 $N\approx K\cdot P$。$K=4$、$P=1600$ 时视觉长度 $N$ 约为 $6.4\mathrm{k}$ 个表示，八层 cross-attn 都能读取，decode 每步还要对它们计算 $QK^{\top}$。$128\mathrm{k}$ 文本窗保留，TTFT、视觉 KV 和 TPOT 仍有成本。

Serving 分别量 encoder 时延、视觉 KV 字节、cross-attn 增加的 TPOT。图不变、只追加文本时可缓存视觉 $K/V$，不重跑 ViT。Batch 的 tile 数不同，要 pad 到 `max_num_tiles` 并正确 mask，否则 $2\times2$ 与 $1\times1$ 的形状对不上。文本 PagedAttention 管文本 self-attention cache，视觉旁路另算，见 `sys-paged-attn`、`meta-vllm`。

网格选错或漏 mask 会让竖图横图质量不稳定；所有图先 pad 正方形再缩到 $224$，容易丢文字。把 $K$ 直接开到 $6\times6$、不改位置编码和训练分布，也可能让 OCR 出错。Haystack 文本长度更不能证明视觉读图的长上下文能力。

## 追问

**为什么不无限切？**
Encoder、视觉长度和延迟都会增加，默认 $K=4$ 是质量成本折中，密集文档与风景图不必用同样块数。

**还需要缩略图吗？**
拼接式 AnyRes 需要全局图辅助理解局部，3.2 则在 vision global 层混合，画架构时要分开。

**多图怎么处理？**
Mllama 按 batch 内最大图数 padding。Guard 3 Vision 公开保证的是每条一张图，多图安全见 `meta-mm-safety`，不能直接假定支持图集。

**NaViT 有什么不同？**
它将可变分辨率图 pack 进同一个 ViT batch；AnyRes / 3.2 tile 选择离散网格，还需区分视觉 token 是否进入 LM 窗口。
