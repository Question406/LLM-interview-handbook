---
id: sys-overlong
section: systems
order: 22
level: S
title: 系统：超长序列的激活、注意力时间、并行怎么叠
quick: "激活随 $B\\cdot T\\cdot L\\cdot h$ 涨，注意力 FLOPs 随 $T^2$ 涨，TP 不切 $T$ 所以帮不上。先开 Flash、activation checkpoint 和 SP，仍不够再上 Ulysses 或 ring CP。"
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

## 题怎么来的

NVIDIA 长上下文预训练、Microsoft Ulysses、Anthropic / Google 的 100k+ 窗口，都会问「$T$ 拉长时先爆哪、加哪一种并行」。这不是再背一张 3D 表。三维切的是样本、层内矩阵、深度，见 `sys-3d-parallel`。超长 $T$ 是第四轴：激活显存和注意力计算时间可能比参数存储更早成为瓶颈。

## 两堵墙：HBM 和 $T^2$

不 checkpoint 时，残差和 MLP 中间结果跟 $B\cdot T\cdot L\cdot h$ 走。ZeRO 再怎么切状态也碰不到它。FlashAttention 已经不把 $[B,H,T,T]$ 分数写回 HBM，所以「注意力矩阵爆显存」经常是过时说法；真正还在涨的是每层激活和 KV 工作区。Selective checkpoint 把便宜算子重算，大 GEMM 能存就存，见 `sys-act-checkpoint`。

实际耗时另一侧：朴素注意力 $O(T^2 d)$。$T$ 从 4k 到 128k 是 32 倍长度、大约 1000 倍注意力 FLOPs。Flash 改善 HBM 流量，不改变 FLOPs 的 $T^2$。MLP 是 $O(T d^2)$，足够长之后注意力重新主导 step time。面试要分开说：显存账和算力账不是同一张图。

数量级：$h=4096$，$L=32$，$B=1$，$T=128\mathrm{k}$，BF16 残差流大约 $2\cdot T\cdot L\cdot h$ 已是数十 GB 级，还没算 MLP 的 $4h$ 中间项。单卡放不下是正常的，不是实现没写好。

## 根据瓶颈选择并行方式

不要加 TP 来「切长序列」。TP 切的是 $h$ 和头，激活的 $T$ 维在纯 TP 下是完整的；SP 才把 LN/dropout 的 $T$ 切开，且必须绑 TP，见 `sys-seq-parallel`。注意力仍要完整 $T$（每卡本地那几头）。

按顺序我会这样开：

1. **FlashAttention + 合理 microbatch。** 先把分数矩阵移出 HBM。
2. **Activation checkpoint（selective）。** 用于减少激活显存。
3. **Megatron SP。** 有 TP 时砍复制的 LN 激活。通信字节不降，内存降。
4. **还是装不下完整 $T$ 的注意力工作区：** Context parallel / ring，Q 本地、KV 环传，见 `sys-context-parallel`。因果 mask 要 zigzag。
5. **头够、NVLink 域、想要 all-to-all：** Ulysses，序列切 $\leftrightarrow$ 头切，见 `sys-ulysses`。头不够（GQA+TP）别硬开。
6. **深度仍放不下：** PP。气泡公式在长 $T$、重算变慢后要重算一遍，见 `nvidia-pipeline-bubble`。
7. **状态爆、激活还好：** ZeRO。对超长 $T$ 通常不是第一步，见 `sys-zero-stages`。

层次组合常见：节点内 Ulysses（NVLink all-to-all）+ 跨节点 ring。Megatron CP 的 `a2a+p2p` 就是这个意思。EP 解决专家，不切 $T$，见 `sys-expert-parallel`。

推理侧超长序列的瓶颈是 KV 容量和处理输入的 prefill 时间：分页、KV 量化、chunked prefill 或 PD 分离，不是再套一份训练 CP 到在线逐 token 生成（decode）上，见 `sys-paged-attn`、`sys-chunked-prefill`。

错误切法：纯 DP 撑 128k（激活先炸）；把 TP 开到 64 跨 IB（通信墙，见 `sys-tp-overlap`）；只开 SP 以为注意力也切了；Ulysses 度数大于 KV 头。

## 追问

- **Flash 之后为什么还要 CP？** Flash 管单卡 IO 和分数矩阵。$T$ 大到单卡放不下 QKV/激活，仍要沿序列切卡。
- **Ulysses 和 ring 怎么选？** 头够且高速互联，A2A 往往更好。头不够或跨 IB，ring。可以分层。
- **checkpoint 能替代序列并行吗？** 不能。一个减段内张量，一个减跨卡复制或切 $T$。长上下文经常两件一起开。
- **batch 减到 1 够吗？** $T$ 足够大时 $B=1$ 激活仍爆，注意力仍 $T^2$。减 $B$ 只是第一步，不是终点。
