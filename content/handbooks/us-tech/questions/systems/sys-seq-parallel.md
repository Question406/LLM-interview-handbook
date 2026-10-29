---
id: sys-seq-parallel
section: systems
order: 4
level: A
title: 系统：sequence parallel 减 activation，和 TP 的配对
quick: >-
  Megatron SP 配合 TP，把 LayerNorm / dropout 的激活沿序列分摊：列并行前 all-gather，行并行后
  reduce-scatter。它减少复制的激活，通信字节仍与原 all-reduce 同阶；将 attention
  计算本身沿序列切开，则属于另一类上下文并行。
tags:
  - NVIDIA
  - Megatron
  - Sequence Parallel
  - Tensor Parallel
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: 'https://arxiv.org/abs/2205.05198'
    type: primary
  - title: Sequence Parallelism — Long Sequence Training from System Perspective
    url: 'https://arxiv.org/abs/2105.13120'
    type: primary
  - title: Megatron-LM
    url: 'https://arxiv.org/abs/1909.08053'
    type: primary
  - title: >-
      Efficient Large-Scale Language Model Training on GPU Clusters Using
      Megatron-LM
    url: 'https://arxiv.org/abs/2104.04473'
    type: primary
---

Megatron 的 sequence parallel 主要减少 TP 中重复保存的激活：LayerNorm、dropout 沿序列切分，每卡只保留一段，进出 TP 矩阵计算时再切换布局。它需要配合 TP，attention 本身仍按 Megatron 的头和矩阵切法计算。

纯 TP 中，列并行 GEMM 的输入是完整 $[B,T,h]$。行并行输出做完 all-reduce 后，各 TP rank 都保存同一份 LayerNorm / dropout 激活，长序列时这份复制会占很多 HBM。SP 让局部算子只持有 $[B, T/\mathrm{TP}, h]$，列并行前用 all-gather 拼回完整 $T$，行并行后用 reduce-scatter 代替 all-reduce，只取回本卡负责的序列段。

这样相关激活按 TP 倍数减少，通信仍是 $B\cdot T\cdot h$ 量级，AG + RS 与原 all-reduce 字节同阶。`sequence_parallel` 通常要求 TP 度大于 $1$，SP 组就是 TP 组，gather/scatter 才对得上 hidden 的切分。没有 TP，也就没有这份复制的 LN 激活可省。Nsight 中 NCCL 时间不会因为开 SP 自动消失。

SP 与 checkpoint 可以一起开：前者去掉 TP 中的激活复制，后者减少为大 GEMM 保存的段内中间结果，见 `sys-act-checkpoint`。FlashAttention 不再写回 attention 分数后，SP 的收益更集中在 LN / MLP 周围。

## 另一种同名的序列并行

Google / Colossal-AI 的 Sequence Parallelism（arXiv:2105.13120，Li et al.）、Ring Attention、NVIDIA context parallel 切的是 attention $QK^{\top}$ 的序列轴。每卡处理一段 query，再通过环传或 all-gather 取得 KV，解决完整 $T$ 放不进单卡的问题。它可以与 TP 正交组成 DP、TP、PP、CP 四维，通信随 $T\cdot h_{\mathrm{kv}}$ 增长。

所以被问“sequence parallel 减 activation”时，我会先确认语境：NVIDIA / Megatron 的 `sequence_parallel=True` 通常指配合 TP 的 LN/dropout 布局；Google 长上下文及上述论文更可能指切 attention 的序列维。前者不会切样本，也不能替代 PP；深度放不下仍需切层，超长 attention 工作区放不下仍需 CP / ring。三维分工见 `sys-3d-parallel`，列并行与行并行见 `nvidia-tensor-parallel`。

EP 与 TP 同时开时，Megatron 会建议开 SP，减少 expert 路径的激活复制，见 `sys-expert-parallel`。

## 追问

**SP 省通信还是内存？**
主要省内存。All-reduce 换成 all-gather 加 reduce-scatter，字节量相近，延迟特征会变。

**为什么和 TP 用同一组？**
布局切换直接服务 TP ranks，换组就对不上 hidden 切分。

**只加 SP 能撑超长上下文吗？**
不一定。Megatron SP 不拆 attention 计算，单卡仍装不下时，要沿 $T$ 做 context parallel 或 ring。

**先开 SP 还是 ZeRO？**
先看瓶颈：激活超限用 SP 加 checkpoint，模型状态超限用 ZeRO，见 `sys-zero-stages`。
