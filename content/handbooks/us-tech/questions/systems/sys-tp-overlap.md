---
id: sys-tp-overlap
section: systems
order: 20
level: A
title: 系统：TP 通信和 GEMM overlap，怎么暴露通信墙
quick: "TP 层内通信往往在关键路径上，需要把 GEMM 分块，让已完成块的通信与下一块计算重叠。先估计算和通信的时间比，再在 Nsight 中看 NCCL 与 MMA 是否同时有效工作；TP 太大或跨慢链路时，单开 overlap 未必有益。"
tags:
  - NVIDIA
  - Megatron
  - Tensor Parallel
  - NCCL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM
    url: https://arxiv.org/abs/2104.04473
    type: primary
  - title: Megatron-LM — Training Multi-Billion Parameter Language Models Using Model Parallelism
    url: https://arxiv.org/abs/1909.08053
    type: primary
  - title: NCCL Collective Operations
    url: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/operations.html
    type: secondary
  - title: NVIDIA Transformer Engine
    url: https://github.com/NVIDIA/TransformerEngine
    type: primary
---

TP 通信要与 GEMM 重叠，必须先找到不互相依赖的计算块：一块算完就开始传，另一块继续计算。默认的层内 all-reduce 会挡住后续残差和 LN，因此不能只开一个 overlap 开关就认为成本消失。

先估它是否会成为瓶颈。一层正向有两次行并行 all-reduce，payload 都是 $[B,T,h]$ 量级，BF16 约 $2BTh$ 字节。MLP 两个 GEMM 的计算约为 $16BTh^{2}/\mathrm{TP}$ FLOPs，计算与通信时间比近似为：

$$
\frac{T_{\mathrm{gemm}}}{T_{\mathrm{ar}}}\propto \frac{h}{\mathrm{TP}}\cdot\frac{\mathrm{NVLink}}{\mathrm{peak}}.
$$

$B$、$T$ 在两边同阶相消，拉长序列并不会单独改善这个比。TP 过大使 $h/\mathrm{TP}$ 变小，或链路从 NVLink 降为 IB，比值小于 1 就更受通信限制。节点内 TP$=8$、$h=8192$ 往往仍以计算为主，跨节点带宽低一个数量级，MFU 会先下降，见 `sys-3d-parallel`。

SP 把 all-reduce 换成 all-gather + reduce-scatter，字节仍同阶，只是提供了不同的重叠机会，见 `sys-seq-parallel`、`sys-allreduce-reducescatter`。TP 切法和 NCCL 基础分别见 `nvidia-tensor-parallel`、`nvidia-nccl-allreduce`，Megatron / Transformer Engine 的 userbuffer 讨论建立在这些依赖上。

## 怎样重叠，怎样确认有效

默认路径是行并行 GEMM $\to$ all-reduce $\to$ 残差和 LN，后者需要完整向量。可以沿序列或 batch 分波计算，第一波开始 AR 时继续算第二波。SP 下也可让列并行需要的 AG 与相邻无依赖计算重叠，让 RS 与已经本地可算的 dgrad 重叠。Transformer Engine userbuffer / P2P 预留通信缓冲和 SM，减少与 MMA 争用资源。

块切得太碎会增加启动开销，太大则仍是先算后传；`cudaDeviceSynchronize` 或默认 stream 也可能把路径串行化。即使时间线重叠，NCCL 与 GEMM 抢 SM 仍可能让两者一起变慢。反向的激活梯度与权重梯度依赖不同，也不能照搬正向切法。DP 梯度 AR 较容易藏在前几层 backward 后，TP 层内 AR 则需要更细的调度；PP P2P 重叠不足会表现为气泡，见 `nvidia-pipeline-bubble`。

Nsight Systems 中，看 `ncclDevKernel` 与 MMA 是否并行且 GPU 持续有效工作。如果两者之间有空档、GPU 在等，就是通信暴露在关键路径；若重叠时 SOL 都低，可能是资源竞争。单报“NCCL 占 30%”不够，要判断这段时间能否藏到计算下面。

通信已经受限时继续加 TP 会增加负担，关 SP 也没减少字节，ZeRO-3 还会加每层 AG。更直接的选择是减 TP、提高 $h$ 方向的算术强度，或把 TP 收回节点内。

## 追问

**长 $T$ 为什么救不了 TP？**
GEMM 和 AR 都随 $T$ 线性增长，主要比的是 $h/\mathrm{TP}$ 与链路带宽。

**SP 的 AG + RS 更好重叠吗？**
有机会，能分别配对相邻 GEMM，但字节同阶，收益仍要测。

**Userbuffer 是什么？**
预留给通信使用的显存和 SM，减少与计算 kernel 的竞争。细节随 TE 版本变化，先说清这个目的。

**推理 TP 呢？**
Decode 的 GEMM 更瘦，层内 AR 更容易成为瓶颈，serving 的 TP 往往更保守，也可能改用 EP 或复制。
