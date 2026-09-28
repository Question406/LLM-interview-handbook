---
id: sys-seq-parallel
section: systems
order: 4
level: A
title: 系统：sequence parallel 减 activation，和 TP 的配对
quick: >-
  Megatron SP 不替代 TP：LayerNorm / dropout 按 $T$ 切开，进列并行前 all-gather，出行并行后
  reduce-scatter。激活按 TP 倍降，集体通信体积和原来的 all-reduce 同量级。另一路是把注意力本身按序列切，那是上下文并行。
tags:
  - NVIDIA
  - Megatron
  - Sequence Parallel
  - Tensor Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: https://arxiv.org/abs/2205.05198
    type: primary
  - title: Sequence Parallelism — Long Sequence Training from System Perspective
    url: https://arxiv.org/abs/2105.13120
    type: primary
  - title: Megatron-LM
    url: https://arxiv.org/abs/1909.08053
    type: primary
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
---

## 题怎么来的

NVIDIA 训长序列、Megatron Core 的 `sequence_parallel=True`，几乎总会追 SP 和 TP 什么关系。Google / Colossal-AI 那篇 Sequence Parallelism（arXiv:2105.13120）讲的是另一刀：把注意力计算按序列切开。两个都叫 sequence parallel，面试先划清，否则评委会以为你把 Megatron 开关和环状 KV 传混了。

## Megatron SP：补 TP 留下的复制

纯张量并行里，列并行 GEMM 要完整序列上的 $[B,T,h]$，行并行输出 all-reduce 之后，LayerNorm 和 dropout 在每个 TP rank 上是同一份完整激活。这部分显存不随 TP 下降，长 $T$ 时它就是激活墙。

SP 的修法：这些序列局部算子按 $T$ 维切开，每卡只持有 $[B, T/\mathrm{TP}, h]$。布局切换夹在 TP GEMM 两侧：

1. 列并行之前：all-gather 把序列拼回完整 $T$，满足 Megatron 列并行对输入的假设。
2. 行并行之后：reduce-scatter 代替 all-reduce，每卡只拿回自己那一段序列。

通信体积和原来的层内 all-reduce 同量级（还是 $B\cdot T\cdot h$ 量级的集体通信），但落盘激活除以 TP。代码里通常强制 `sequence_parallel` 必须张量并行度大于 $1$，因为 SP 组就是 TP 组。没有 TP 就没有「复制的 LN 激活」这件浪费，开 SP 没有对象。

和 checkpoint 的分工：SP 砍的是被 TP 复制的那一份；checkpoint 砍的是段内为大 GEMM 留下的中间结果。长上下文两件一起开，见 `sys-act-checkpoint`。FlashAttention 之后，注意力分数不再写 HBM，SP 的收益更集中在 LN / MLP 周围的激活。

## 另一路：把注意力按序列切开

Li et al. 的 Sequence Parallelism、Ring Attention、NVIDIA 后来的 context parallel，切的是 $QK^{\top}$ 本身：每卡只算一段 query，KV 沿环或 all-gather 凑齐。它解决的是单卡放不下 $T$，不是 TP 复制。可以和 TP 组正交（四维：DP、TP、PP、CP），通信是 KV 块的点对点或集体，体积跟 $T\cdot h_{\mathrm{kv}}$ 走。

面试对照一句话：

- Megatron SP：和 TP 绑死，改的是 LN/dropout 的内存布局，GEMM 仍按 Megatron 列/行切。
- Context / 环状 SP：切注意力的序列轴，通信是 KV 搬家，目的是更长 $T$。

评委说「sequence parallel 减 activation」，NVIDIA 语境默认第一句；Google 长上下文和 2105.13120 默认第二句。问清再往下画。三维切分怎么给 SP/CP 留位置，见 `sys-3d-parallel`；和 TP 的列/行切法对着看 `nvidia-tensor-parallel`。

一个常见错觉：开了 SP，层内通信量「消失了」。没有。AG+RS 的字节量和原来的 all-reduce 同阶，只是内存布局变了。Nsight 上 NCCL 时间不会 magically 归零；省下的是 HBM 里那份复制的 LN 激活。

错误配对：只开 SP 不开 TP（Megatron 会直接拒）；把 SP 当 DP（样本没切）；以为 SP 能替代 PP（深度放不下仍要切层）。EP 和 TP 同时开时，Megatron 会警告最好打开 SP，否则 expert 路径上的激活复制更难看，见 `sys-expert-parallel`。

## 追问

- **SP 省的通信还是内存？** 主收益是内存。集体通信从 all-reduce 换成 all-gather 加 reduce-scatter，字节量相近，延迟特征略不同。
- **为什么必须和 TP 一组？** 布局切换的 gather/scatter 对端就是 TP ranks。换一组对不齐 hidden 切分。
- **超长上下文只加 SP 够吗？** Megatron SP 不拆注意力计算。$T$ 大到单卡注意力放不下，要 context parallel 或 ring，或把 $T$ 再切。
- **和 ZeRO 谁先开？** 激活爆开 SP 加 checkpoint；状态爆开 ZeRO。两味药对两类病，见 `sys-zero-stages`。
