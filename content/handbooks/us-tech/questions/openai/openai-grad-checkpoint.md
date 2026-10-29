---
id: openai-grad-checkpoint
section: openai
order: 14
level: A
title: OpenAI：activation checkpoint 省显存的代价，和 ZeRO 怎么叠
quick: "Checkpoint 只保存段界激活，反向时重算中间结果，用额外计算换显存；ZeRO 则分片参数、梯度和优化器状态。先看是哪类显存超预算，长上下文训练常需要同时使用两者。"
tags:
  - OpenAI
  - Gradient Checkpointing
  - ZeRO
  - Memory
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training Deep Nets with Sublinear Memory Cost
    url: https://arxiv.org/abs/1604.06174
    type: primary
  - title: ZeRO — Memory Optimizations Toward Training Trillion Parameter Models
    url: https://arxiv.org/abs/1910.02054
    type: primary
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

Activation checkpointing 用重计算减少激活显存，ZeRO 分片模型状态，两者能叠加。比如同一份 7B bf16 模型，ZeRO-2 已把 Adam 状态分摊到多卡，长上下文仍可能 OOM，因为每张卡还要留自己 microbatch 的激活。

Transformer 前向要为每层反向保留激活，总量随 $B\cdot T\cdot L\cdot d$ 增长。checkpoint 只存段界输入，反向进入一段时再前向计算其中激活。每层都重算时，前向粗占 fwd+bwd 的三分之一，实际时间常多 20%–40%，约 $+30\%$ 量级。每 $\sqrt{L}$ 层存一次是论文的亚线性方案，激活可从 $O(L)$ 降到 $O(\sqrt{L})$；按每层 checkpoint 则保留每层常数的入口存储，不能把入口一起丢掉。

选择性 checkpoint 会按算子划分，比如重算 attention、FFN，留下 LayerNorm、残差短连接。FlashAttention 已避免在 HBM 留完整 `[B,H,T,T]` 分数，它只覆盖 attention，与其他段的重算仍可配合。这是训练图中的重计算边，和 `torch.no_grad` 不同。

把显存账写具体：$B=2$、$T=8\mathrm{k}$、$L=32$、$d=4096$，仅每层一份 hidden 就有 $B T L d \times 2$ 字节、数 GB，attention 和 FFN 还会增加。Adam 状态约 $12$ 字节/参数，7B 就是 $\approx 84$ GB。ZeRO-1 切优化器，ZeRO-2 再切梯度，ZeRO-3 连参数一起切、用前 all-gather；它们主要随参数量增长，checkpoint 省的则随 $B,T,L$ 增长。

选方法时先测两列：短上下文大模型，优先用 ZeRO、张量并行装下状态；上下文拉长，ZeRO-3 后仍爆且参数已少，就查激活。一起用时 gather 和重计算都增加时间、降低 MFU，可以尝试通信重叠、更粗的段来隐藏额外前向。纯加数据并行卡数不会减少每卡 microbatch 的激活，超长 $T$ 还要考虑序列并行。

训练每步是完整 $T$ 的前向，没有推理逐 token decode。packing 减少 padding，峰值仍受最长 packed 序列影响，checkpoint 处理的就是这个峰值。

## 追问

**推理要 checkpoint 吗？**
通常不要，decode 没有整段反向。

**gradient accumulation 能降低峰值吗？**
它控制等效 batch，单步激活峰值仍由 microbatch 的 $B,T$ 决定。

**offload 能代替吗？**
CPU/NVMe offload 适合参数和优化器，激活往返更吃带宽，长 $T$ 优先考虑重算。

**MoE 的段怎么划？**
可划在路由之后，避免重算又做一遍 all-to-all。

相关：`nvidia-trillion-train`、`openai-adamw`、`openai-prefill-decode`、`openai-moe-aux-loss`
