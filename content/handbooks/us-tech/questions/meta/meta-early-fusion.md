---
id: meta-early-fusion
section: meta
order: 27
level: A
title: Meta：early vs late fusion，Chameleon 一类公开叙事能讲到哪
quick: "Chameleon 将图像 VQ 成离散 token，与文本从第一层共享因果 Transformer，可以生成交错图文。LLaVA 拼接连续视觉向量，Llama 3.2 则用独立视觉塔和 cross-attn 复用 LM，输出文本；选择时要看是否需要出图、OCR 质量和从零训练成本。"
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

早融合把图文从第一层起放进同一条 token 流，适合交错图文生成；外挂视觉塔与 cross-attn 则更方便复用已有语言模型。Chameleon 与 Llama 3.2 是两条不同公开路线，不能把后者直接说成前者的产品版。

Chameleon（2024-05）从零训练，用基于 Make-a-Scene 一类 VQ 的图像 tokenizer，把 $512\times512\to 1024$ 个图像码，码本 $8192$，放进约 $65\mathrm{k}$ 词表。同一因果 Transformer 读纯文、图文对、交错文档，next-token 同时预测词和图像码，因此论文支持出图；开源推理长期未放图像解码器，论文能力与权重发布要区分。公开训练混合约 $10\mathrm{T}$，34B 看到的 token 约为 Llama 2 的 $5\times$。

LLaVA 将 ViT 连续向量经 MLP 投到 LM 维，在 prompt 前面或占位符处接入，从 embedding 层进入主干自注意力。它可复用 LM 与 CLIP、实现简单，通常不能生成像素，视觉 token 占上下文，见 `meta-anyres`。这类连续拼接不宜直接和独立 cross-attn 的晚融合混为一谈。

Flamingo、Llama 3.2 则让独立视觉塔的表示通过 gated cross-attn 供 LM 读取。3.2（2024-09）冻结 3.1 LM、加 adapter，便于保留文本质量并作 drop-in，发布为文本输出，不能自回归生成图像码；视觉推理也受冻结语言表示限制。接法见 `meta-llama-vision`，Gemini 的原生交错见 `google-gemini-mm`。

## 早融合的训练与信息瓶颈

Chameleon 报告直接沿用 Llama 2 栈混模态，到 $8\mathrm{B}$ / $1\mathrm{T}$ 后会在中后期不稳定。论文将其与 softmax 平移不变、图文熵差及范数增长联系起来，bf16 难以承受不断漂移的数值。

QK-Norm 在 attention 中对 $Q,K$ 做 LayerNorm，控制 softmax 输入范数，7B 消融没有它约 $20\%$ epoch 就发散。34B 用 Swin 式先 attn 再 norm 的重排，限制 SwiGLU 放大残差范数。另有 $10^{-5}\log^2 Z$ 的 Z-loss 控制最后 partition function、减轻 logit drift；7B 受益于 $0.1$ dropout，34B 在 norm 重排后去掉 dropout。这些是公开稳定训练结果，不能据此声称内部也采用同一配置。去掉图像生成的消融更稳，出图增加了训练难度。

VQ 还会丢信息。论文指出含大量文字的图重建较差，OCR 或截图笔画已经丢失，再大的 LM 也难补回。3.2 的连续 ViT 加切块更适合读文档；Chameleon 的收益在同一模型写交错图文，长文档人评中与 GPT-4V / Gemini-Pro 比较也有竞争力。出图同时引入有害图像生成风险，需多模态安全检查，不能只套文本 Guard，见 `meta-mm-safety`。

选择时我会先确认是否要生成图、能否接受从零训练，以及 OCR 是否主任务。只需看图说话并保留 405B/70B 文本能力，可考虑 3.2；需要文档插图后继续写，才更贴近 Chameleon，同时说明 QK-Norm 与 VQ-OCR 取舍，不承诺未发布的统一权重。

## 追问

**早融合一定更好吗？**
交错生成和跨模态梯度是优点，复用 LM、稳定训练与读小字则可能用拼接或晚融合更便宜。

**解冻 3.2 LM 就成早融合吗？**
不会，两路表示仍经 cross-attn 交互，架构没有变成从第一层共享 token 流。

**离散 token 能加 CLIP 吗？**
能作辅助，但 Chameleon 主目标仍是统一 next-token，不能与对比学习混为一谈。

**为什么不直接用同一权重？**
公开时间线和目标不同，一个从零约 $10\mathrm{T}$ 混模态训练，一个在 3.1 上加 adapter，没有依据推断合并计划。

**位置编码怎么处理？**
图像二维栅格展成一维，再与文本 1D RoPE 共用注意力，是早融合要设计的部分；3.2 把二维处理留在 ViT，LM cross-attn 不用 RoPE。
