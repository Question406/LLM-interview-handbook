---
id: sys-tp-overlap
section: systems
order: 20
level: A
title: 系统：TP 通信和 GEMM overlap，怎么暴露通信墙
quick: >-
  层内 all-reduce 默认在关键路径上：下一层 LN 要完整激活。能藏的办法是把 GEMM 切块，一块在算、一块在传。藏不住时墙
  钟跟 NVLink/IB 走，不是跟 Tensor Core 走。Nsight 上看 NCCL 和 MMA 是并排还是一条缝。
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

## 题怎么来的

NVIDIA 训练岗在 `nvidia-tensor-parallel` 和 `nvidia-nccl-allreduce` 之后会追：这两次层内 all-reduce 到底叠进 GEMM 没有。Megatron / Transformer Engine 的 userbuffer overlap、序列并行下的 AG/RS 切块，问的都是通信墙有没有露出来。我会先写体积和时间比，再讲 overlap 的依赖，不先报一个开关名。

## 先算会不会成为墙

一层正向两次行并行 all-reduce，payload 都是 $[B,T,h]$ 量级。BF16 字节 $2BTh$。MLP 计算大约 $16BTh^{2}/\mathrm{TP}$ FLOPs（上下两个 GEMM，按 TP 切开）。计算/通信时间比近似

$$
\frac{T_{\mathrm{gemm}}}{T_{\mathrm{ar}}}\propto \frac{h}{\mathrm{TP}}\cdot\frac{\mathrm{NVLink}}{\mathrm{peak}}.
$$

和 $B$、$T$ 同阶相消：**长序列不会让 TP 更划算**，两边一起涨。$h/\mathrm{TP}$ 变小（TP 过大）、或带宽掉到 IB，比值小于 1，就是通信墙。节点内 TP$=8$、$h=8192$ 往往还是计算主导；跨节点 TP，带宽掉一位，MFU 先死。这就是「TP 锁 NVLink 域」的数量级版，见 `sys-3d-parallel`。

SP 把 all-reduce 换成 all-gather + reduce-scatter，字节同阶，只是布局变了，见 `sys-seq-parallel`、`sys-allreduce-reducescatter`。墙还在，只是变成 AG 能否和下一截 GEMM 叠。

## Overlap 怎么做、为什么经常叠不上

默认实现：行并行 GEMM 结束 $\to$ all-reduce $\to$ 残差和 LN。LN 依赖完整向量，通信在关键路径上。Overlap 要把 **没有数据依赖的那一块** 和通信并起来：

- 沿序列或 batch 把 GEMM 切成几波：第一波算完先发 AR，第二波 GEMM 和第一波 AR 重叠。
- SP 下：列并行需要的 all-gather 可以和下一段无关计算叠；reduce-scatter 可以和已经本地的 dgrad 叠。
- Transformer Engine 的 userbuffer / P2P 把 NCCL 缓冲钉在通信专用 SM 上，减少和 MMA 抢寄存器。

叠不上的常见原因：切得太碎，启动次数吃掉带宽；切得太整，仍是先算完再传；`cudaDeviceSynchronize` 或默认 stream 把 NCCL 和 GEMM 串起来；NCCL 和 GEMM 抢 SM，两个都慢。反向更烦：激活梯度和权重梯度的依赖不同，不能照抄正向切块。

DP 梯度 AR 容易藏在前几层 backward 后面；TP 层内 AR 默认藏不住。面试把两者说成「都 overlap 就好」会穿帮。PP 的 P2P 体积小，叠不上表现为气泡，见 `nvidia-pipeline-bubble`。

## 怎么在 Nsight 上暴露墙

Systems 时间线：`ncclDevKernel` 和 MMA 并排且 GPU 忙，overlap 在工作。一条缝、GPU 空，就是等通信——墙露出来了。两者重叠但 SOL 都很低，是抢 SM，再加 overlap 会更差，该减 TP 或把通信移回 NVLink。不要只报「NCCL 占 30%」：要说这 30% 能不能挪到计算底下。

错误处方：通信墙了就加 TP（墙更厚）；墙了就关 SP（字节没少）；墙了就开 ZeRO-3（又加每层 AG）。对症是减小 TP、加大 $h$ 方向的算术强度、或把 TP 缩回节点内。

## 追问

- **为什么长 $T$ 救不了 TP 通信比？** GEMM 和 AR 都线性于 $T$，比值跟 $h/\mathrm{TP}$ 和链路带宽走。
- **SP 的 AG+RS 比 AR 更好叠吗？** 有机会，因为两端可以分别和相邻 GEMM 配对。不是免费，字节同阶。
- **Userbuffer 是什么？** 预留一块给 NCCL 的显存和 SM，避免和计算 kernel 抢。实现细节随 TE 版本变，面试讲意图即可。
- **推理 TP 也要 overlap 吗？** Decode 一步 GEMM 很瘦，层内 AR 更容易露墙。所以 serving 的 TP 往往比训练更保守，或改 EP/复制。
