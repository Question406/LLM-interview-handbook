---
id: meta-early-fusion
section: meta
order: 27
level: A
title: Meta：early vs late fusion，Chameleon 一类公开叙事能讲到哪
quick: "早融合如 Chameleon，把图 VQ 成离散 token，和文本从第一层共用一条 Transformer，能生成交错图文。晚融合如 Llama 3.2，独立视觉塔加 cross-attn，只能输出文本。"
tags:
  - Meta
  - Chameleon
  - Multimodal
  - Fusion
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Chameleon — Mixed-Modal Early-Fusion Foundation Models
    url: https://arxiv.org/abs/2405.09818
    type: primary
  - title: Llama 3.2 vision blog
    url: https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/
    type: primary
  - title: Flamingo — a Visual Language Model for Few-Shot Learning
    url: https://arxiv.org/abs/2204.14198
    type: secondary
  - title: Visual Instruction Tuning (LLaVA)
    url: https://arxiv.org/abs/2304.08485
    type: secondary
---

FAIR / Llama 岗爱把融合画成谱，看你知不知道 **3.2 Vision 和 Chameleon 不是同一条发布线**。Chameleon（2024-05）是从零训练的 token 早融合，图文都能生成；3.2（2024-09）是冻住 3.1、外挂 cross-attn，只出文本。公开能讲到架构、稳定性和取舍；不要说成「公司内部已经统一成一种」。Gemini 原生交错见 `google-gemini-mm`，3.2 接法见 `meta-llama-vision`。

## 三条公开做法

**离散早融合（Chameleon）。** 图像 tokenizer（论文：基于 Make-a-Scene 一类 VQ，$512\times512\to 1024$ 个码，码本 $8192$）把图变成和词一样的离散 id。词表约 $65\mathrm{k}$，里面含这 $8192$ 个图像码。同一条因果 Transformer，序列可以是纯文、图文对、交错文档。Next-token 既预测词也预测图像码，所以 **能生成图**（开源推理长期没放图像解码器，面试要说「论文能力 vs 权重发布」）。数据公开量级：约 $10\mathrm{T}$ 交错混合，34B 看到的 token 大约是 Llama 2 的 $5\times$。

**连续拼接（LLaVA）。** ViT 连续向量经 MLP 投到 LM 维，接到 输入提示（prompt） 前面或占位符处，之后全是自注意力。实现简单、能复用现成 LM 和 CLIP。图通常 **不能** 当像素生成。视觉 token 直接吃上下文窗，见 `meta-anyres`。

**晚融合 / adapter（Flamingo、Llama 3.2）。** 视觉塔独立；LM 用 gated cross-attn 读图。3.2 冻 LM，文本基准不易塌，发版是 3.1 的 drop-in。**不能** 自回归出图像 token。视觉推理的上限受冻住的语言表示约束。

常见误区是：把 LLaVA 叫晚融合：视觉从 embedding 层就进主干，只是连续向量不是 VQ。错法二：把 3.2 叫 Chameleon 的产品化：训练目标、能否出图、是否复用 3.1，三条都反。

## 早融合为什么难训，论文写了什么

Chameleon 说按 Llama 2 栈直接混模态，到 $8\mathrm{B}$ / $1\mathrm{T}$ 以后会在中后期炸掉。原因他们归到 **softmax 平移不变**：图和文熵差大，共享权重的模态会靠抬范数抢 softmax，bf16 撑不住就散。公开的稳定训练方法包括：

- **QK-Norm**：attention 里对 $Q,K$ 做 LayerNorm，按住送进 softmax 的范数。7B 消融显示没它大约 $20\%$ epoch 就散。
- **Norm 重排（34B）：** Swin 式先 attn 再 norm，限制 SwiGLU 把残差范数乘飞。
- **Z-loss：** $10^{-5}\log^2 Z$ 按住最后一层 partition function，减轻 logit drift。
- Dropout $0.1$ 帮过 7B；34B 用 norm 重排就去掉 dropout。

这些是 **公开稳定性叙事**，不是让你现场保证「我们内部也这样」。没有图像生成的消融更稳；出图是早融合贵的那一半。

VQ 的硬伤论文自己写了：重建带大量文字的图很差，所以 **OCR / 读截图被 tokenizer 封顶**，再大的 LM 也读不回已经丢掉的笔画。3.2 用连续 ViT + 切块，读文档更像产品选择。Chameleon 的交换物是：同一模型写交错图文、人评长文档里对 GPT-4V / Gemini-Pro 不丢面。安全：早融合能出图，有害图像生成是新面，不能只套文本 Llama Guard，见 `meta-mm-safety`。

## 现场怎么选

我会按产品问三句：要不要生成图像；能不能接受从零训、不复用 3.1；OCR 是不是主任务。只要「看图说话 + 保住 405B/70B 文本质量」，走 3.2。要「文档里插图再接着写」，Chameleon 叙事才对口，并主动报 QK-Norm 和 VQ-OCR。不要许诺未发布的统一权重。

## 追问

- **早融合一定更好吗？** 交错生成和跨模态梯度是它的好。复用已有 LM、训练稳定、读小字，晚融合或拼接往往更便宜。没有免费的「更原生」。
- **解冻 3.2 的 LM 算不算早融合？** 不算。仍是两条表示、靠 cross-attn 对齐。早融合指 **从第一层起共享同一套 token 流**。
- **离散 token 能接 CLIP 吗？** 能当辅助，但 Chameleon 主损失是统一 next-token。别把对比学习和因果早融合说成一件事。
- **为什么 3.2 不直接用 Chameleon 权重？** 公开时间线和目标都不同：一个从零混模态约 $10\mathrm{T}$，一个在 3.1 上加 adapter。现场不要脑补合并计划。
- **位置编码？** 图像码是二维栅格再展成一维；和文本 1D RoPE 塞进同一注意力，是早融合要单独设计的点。3.2 把二维问题留在 ViT，LM 侧 cross-attn 干脆不用 RoPE。
