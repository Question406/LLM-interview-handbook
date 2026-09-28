---
id: openai-vit-connect
section: openai
order: 28
level: S
title: OpenAI：ViT / patch embed 怎么接到 LLM，投影、对齐预训练、分辨率插值
quick: >-
  连接器把冻住的 ViT patch 从 $D_{\mathrm{vis}}$ 映到 $D_{\mathrm{lm}}$，当普通 token 拼进序列。先对图文对只训投影对齐空间，再指令微调。分辨率要么插值位置编码并微调 ViT，要么按预训练边长切块再拼（LLaVA-HD），不要推理时突然改 patch 数还不改位置。
tags:
  - OpenAI
  - ViT
  - Projector
  - Multimodal
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: An Image is Worth 16x16 Words (ViT)
    url: https://arxiv.org/abs/2010.11929
    type: primary
  - title: Learning Transferable Visual Models From Natural Language Supervision (CLIP)
    url: https://arxiv.org/abs/2103.00020
    type: primary
  - title: Visual Instruction Tuning (LLaVA)
    url: https://arxiv.org/abs/2304.08485
    type: primary
  - title: Improved Baselines with Visual Instruction Tuning (LLaVA-1.5)
    url: https://arxiv.org/abs/2310.03744
    type: primary
  - title: Flamingo — a Visual Language Model for Few-Shot Learning
    url: https://arxiv.org/abs/2204.14198
    type: primary
---

## 题怎么来的

OpenAI 没把 GPT-4o 的视觉塔图纸放出来。面试要的是你能从公开配方搭一条 ViT → 投影 → LLM 的管子，并说清哪一段冻、哪一段更新、分辨率变了位置编码怎么动。原生端到端见 `openai-mm-gpt`；这题是连接器。LLaVA / CLIP / ViT / Flamingo 是能写在白板上的来源，别说成「OpenAI 内部就是 LLaVA」。

## 投影：shape 先对，语义后对

ViT：图 $H\times W$，patch $P$，得到 $N=(H/P)\times(W/P)$ 个 patch，可选 CLS。每个 patch 线性 embed 到 $D_{\mathrm{vis}}$，加二维展平后的位置编码，过 Transformer，取最后一层 patch 特征 $Z\in\mathbb{R}^{N\times D_{\mathrm{vis}}}$（有人丢 CLS，有人留）。

接到 LLM 不是点积检索，是变成词嵌入空间里的向量：

$$
H_{\mathrm{vis}}=W_2\,\sigma(W_1 Z),\qquad W_1\in\mathbb{R}^{D_h\times D_{\mathrm{vis}}},\; W_2\in\mathbb{R}^{D_{\mathrm{lm}}\times D_h}.
$$

LLaVA 原文一层线性；1.5 改两层 MLP + GELU，公开消融说更好。Flatten 成 $N$ 个 token，和文本 embed 在序列维 concat，之后就是普通因果 LM。投影不改变 $N$：分辨率仍由 ViT 的 patch 网格决定。

Flamingo 另一条：Perceiver Resampler 把可变 $N$ 压成固定 $K$ 个 visual token，再交叉注意进 LM，不把几百 patch 全塞进上下文。代价是空间细节；表格、UI 小字通常更吃亏。白板要能说出「保留全部 patch」和「压成固定 $K$」的取舍，不要把 xattn 连接器和 prefix 拼接说成同一种。

```python
def project_patches(z, w1, b1, w2, b2):
    # z: [B, N, D_vis]  ->  [B, N, D_lm]
    h = torch.nn.functional.gelu(z @ w1.T + b1)
    return h @ w2.T + b2
```

错法：把 CLIP 的图文对比向量（一张图一个）直接当视觉 token 序列。对比学习的全局向量没有 patch 网格，读不了「左上角的数字」。要用 ViT 的 patch 特征，或至少 spatial feature map。

## 对齐预训练：先对准空间，再听指令

典型两阶段（LLaVA）：

1. 对齐。冻 ViT 和 LLM，只训投影。数据是图-标题。损失是标题的 next-token。目的：让 $W Z$ 落在 LLM 认识的嵌入流形上。不在这阶段教「请逐步分析」。
2. 视觉指令微调。解开 LLM（或 LoRA），投影继续训；ViT 仍常冻。数据是「图 + 用户问 + 助手答」。GPT-4 给 LLaVA 造过这类对话，那是数据故事，不是说 OpenAI 产品用了这套权重。

冻谁是显存和能力的旋钮。冻 ViT：便宜、稳定，细粒度 OCR / 图表弱。解冻 ViT：视觉表示跟着 LM 损失动，容易吃图文对里的噪声，要更干净的数据。面试别说「必须解冻」或「永远冻」，说任务：要读字就准备解冻或换更高分辨率编码器。

CLIP 预训练已经把 ViT 拉向自然语言，所以当视觉塔很香；纯 ImageNet ViT 接到 LLM 更难对齐。但 CLIP 目标是检索，不是生成；连接器阶段等于用 LM 损失再拉一次。别把 CLIP 对比损失和 LM 交叉熵并成一句「都是多模态训练」。

## 分辨率：插值位置，或按原边长切块

ViT 的位置编码长度等于预训练网格。推理给 672 而预训练 336、patch 14，网格从 $24^2$ 变成 $48^2$，位置表不够长。ViT 论文自己的做法：对 2D 位置嵌入做插值，再在新分辨率上微调。只插值不微调，注意力的相对几何是歪的，高分辨率白给。

LLaVA-1.5-HD 不插值：按编码器原训练边长切成若干 tile，每块独立过 ViT，再把 feature map 拼回大图，并加一张缩小后的全局图特征，减轻切块伪影。LLM 看到的 $N$ 随 tile 数涨。这和 OpenAI API 按砖计费是同一类预算：要细节就复制编码器、加 token，而不是幻想位置插值免费。

AnyRes / 动态分辨率还要把不同 $N$ 的图 pack 进同一 batch，padding 和注意力 mask 按图走，不要用 batch 里最大 $N$ 去给小图旋位置。和文本 packing 同一纪律。

错法：推理改 `image_size` 却不改 pos embed；把所有图 pad 成正方形浪费边；认为插值等于「训练过长上下文」。位置插值只让 ViT 吃得下更多 patch，不自动教会跨 tile 的推理。

## 追问

- **投影维为什么常 $D_{\mathrm{vis}}\to D_{\mathrm{lm}}$ 而不是反过来？** 要进 LM 残差，必须是 $D_{\mathrm{lm}}$。压回 $D_{\mathrm{vis}}$ 再让 LM 自己涨维，等于没对齐。
- **Perceiver 固定 $K$ 能不能随分辨率加大 $K$？** 能，但那是新超参，要对齐阶段重训。宣传「任意分辨率、token 数不变」时，空间信息在压缩里丢。
- **RoPE 怎么加到视觉 token 上？** 拼进 LM 之后走 LM 的位置；视觉塔内部仍用 ViT 的 2D 位置。两套不要混成一个下标。LM 侧下标接在文本后面，见 `openai-rope-offset` 那种 off-by-one。
- **只训投影够不够上产品？** 做 caption 原型够。要指令遵循、拒答、工具，必须有视觉指令数据；对齐阶段不会凭空出现。
