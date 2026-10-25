---
id: sys-overlong
section: systems
order: 22
level: S
title: 系统：超长序列的激活、注意力时间、并行怎么叠
quick: "超长序列要分开算激活显存和注意力计算量：前者随 $B\\cdot T\\cdot L\\cdot h$ 增长，后者随 $T^2$ 增长。先用 FlashAttention、重计算和 Megatron SP 减显存，单卡仍放不下完整序列时，再用 Ulysses 或 ring CP 沿序列切分。"
tags:
  - NVIDIA
  - DeepSpeed
  - Megatron
  - Long Context
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Ring Attention with Blockwise Transformers for Near-Infinite Context
    url: https://arxiv.org/abs/2310.01889
    type: primary
  - title: DeepSpeed Ulysses
    url: https://arxiv.org/abs/2309.14509
    type: primary
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: https://arxiv.org/abs/2205.05198
    type: primary
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention
    url: https://arxiv.org/abs/2205.14135
    type: primary
---

超长序列通常先遇到激活显存和注意力计算量两个瓶颈，单靠切参数解决不了。比如把 $T$ 从 4k 拉到 128k，长度是 32 倍，注意力 FLOPs 却约为原来的 1000 倍。

不做 checkpoint 时，残差和 MLP 中间结果随 $B\cdot T\cdot L\cdot h$ 增长，ZeRO 分摊模型状态碰不到这部分。FlashAttention 不再把 $[B,H,T,T]$ 分数矩阵写回 HBM，但每层激活和 KV 工作区仍在增长。以 $h=4096$、$L=32$、$B=1$、$T=128\mathrm{k}$ 为例，BF16 残差流 $2\cdot T\cdot L\cdot h$ 已是数十 GB，还没算 MLP 的 $4h$ 中间项。Selective checkpoint 可以重算便宜算子、尽量保留大 GEMM 结果，见 `sys-act-checkpoint`。

计算量要另算。注意力是 $O(T^2 d)$，MLP 是 $O(T d^2)$，长度足够大时注意力会重新主导 step time。Flash 减少 HBM 流量，仍保留注意力的 $T^2$ FLOPs。

## 按瓶颈选择并行

我会先开 FlashAttention、调整 microbatch，再加 selective activation checkpoint。有 TP 时加 Megatron SP，把复制的 LN/dropout 激活沿 $T$ 切开。纯 TP 切 $h$ 和头，每卡的注意力仍处理完整 $T$；SP 的通信字节与原来同阶，主要省显存，见 `sys-seq-parallel`。

如果完整序列的注意力工作区仍放不下，就用 context parallel / ring：Q 留在本地，KV 环传，因果 mask 用 zigzag 平衡负载，见 `sys-context-parallel`。头数足够、位于 NVLink 域且适合 all-to-all 时，可选 Ulysses，做序列切分 $\leftrightarrow$ 头切分的布局转换，见 `sys-ulysses`。GQA 再叠 TP 后头数不足，就不能硬加 Ulysses 度数。常见分层组合是节点内 Ulysses、跨节点 ring，Megatron CP 的 `a2a+p2p` 对应这种组合。

深度仍放不下时再加 PP，并按长 $T$ 和重算后的耗时重新估气泡，见 `nvidia-pipeline-bubble`。若主要是状态超限而激活还好，再用 ZeRO，见 `sys-zero-stages`。DP、TP、PP 三维的分工见 `sys-3d-parallel`，EP 负责专家，不切 $T$，见 `sys-expert-parallel`。

这些也是 NVIDIA 长上下文预训练、Microsoft Ulysses、Anthropic / Google 的 100k+ 窗口问题所关心的区别。纯 DP 撑 128k 会先爆激活；TP 开到 64 并跨 IB，可能先碰通信瓶颈，见 `sys-tp-overlap`；只开 SP 也没切注意力本身。推理侧则主要考虑 KV 容量和 prefill 时间，用分页、KV 量化、chunked prefill 或 PD 分离，见 `sys-paged-attn`、`sys-chunked-prefill`，不能直接照搬训练 CP 到在线 decode。

## 追问

**Flash 后为什么还要 CP？**
Flash 解决单卡 I/O 和分数矩阵存储，QKV 与激活大到单卡放不下时，仍要沿序列分卡。

**Ulysses 和 ring 怎么选？**
头数足够且互联快时考虑 A2A；头数不足或跨 IB 时考虑 ring，也可以分层组合。

**checkpoint 能代替序列并行吗？**
不能。它减少段内保存的中间量，序列并行减少复制或把 $T$ 分摊到多卡，长上下文常同时使用。

**batch $B$ 减到 1 够吗？**
不一定。$T$ 足够长时，$B=1$ 的激活也可能超限，注意力仍有 $T^2$ 计算量。
