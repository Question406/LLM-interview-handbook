---
id: nvidia-occupancy
section: nvidia
order: 11
level: S
title: NVIDIA：CUDA occupancy、register 压力，Nsight 上看什么
quick: >-
  Occupancy 是 SM 上在飞的 warp 数除以硬件上限。寄存器每线程太多，能同时住下的 warp 就少，还可能 spill 到
  local memory。它是延迟隐藏的上限，不是速度本身。Nsight Compute 先看 SOL（计算 vs 内存），再看
  theoretical / achieved occupancy、每线程寄存器、spill；Nsight Systems 看有没有核在跑。
tags:
  - NVIDIA
  - CUDA
  - Occupancy
  - Nsight
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: CUDA C++ Programming Guide — Occupancy
    url: https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#occupancy
    type: primary
  - title: Nsight Compute Profiling Guide
    url: https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html
    type: primary
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
---

## 题怎么来的

这是 NVIDIA 岗最本分的 CUDA 题。训练 / 推理系统面也会拐到：为什么 FlashAttention occupancy 不高反而快、为什么 TP 之后 kernel 变碎。我会按 Nsight 的阅读顺序答，而不是背「occupancy 越高越好」。集合通信那侧的空转见 `nvidia-nccl-allreduce`，那是 Systems 时间线；本题是进核之后。

## Occupancy 和寄存器

一个 SM 能同时放的 warp 有上限（架构决定，例如 64）。Occupancy 等于活跃 warp 除以上限。限制来自三条预算同时卡死：

- 每线程寄存器（A100/H100 一个 SM 大约 64K 个 32-bit 寄存器）；
- 每 block 共享内存；
- 每 SM 的 block / warp 槽位。

寄存器例子：64 个寄存器/线程 $\times$ 32 线程/warp $= 2048$ 寄存器/warp。$64\mathrm{K}/2048=32$ 个 warp，上限 64 时 theoretical occupancy 50%。再翻倍到 128 寄存器/线程，只剩 16 个 warp，25%。编译器还会 spill：寄存器不够就把变量放到 local memory（逻辑上每个线程一份，物理上走 HBM），延迟比寄存器差一截。这时 occupancy 数字可能还行，但 long scoreboard 全是在等 spill。

高 occupancy 的唯一好处：有更多 warp 切换，好藏指令延迟和内存延迟。如果 kernel 已经是计算墙且流水线满，再加 warp 不会更快。如果已经是 HBM 墙，需要的是少访存（FlashAttention 那种），不是把 occupancy 刷到 80%。FlashAttention 吃大量 SRAM，theoretical occupancy 往往一般，但 HBM 访问掉一个数量级，墙的位置变了，见 `nvidia-flash-attn`。

`__launch_bounds__`、少 live variable、拆核、用 Occupancy Calculator，都是在和寄存器 / 共享内存做交换。乱加 `__restrict__` 或盲目加大 block，可能把 spill 换来。

## Nsight 上看什么

先 Nsight Systems：GPU 空不空。空，问题在 launch、CPU、NCCL、dataloader，调 occupancy 没有用。核密密麻麻，再下钻 Nsight Compute。

进核以后我按这个顺序说：

1. Speed of Light：SM 吞吐 vs Memory 吞吐。谁先到 70% 以上，谁就是墙。两边都低，才是 occupancy / 指令问题，或者根本没吃到 Tensor Core。
2. Theoretical vs Achieved Occupancy。Theoretical 低：寄存器或 shared memory 预算。Achieved 明显低于 theoretical：warp 在 barrier 上等、block 太少、grid 太瘦（decode 一步那种）。
3. Registers Per Thread、Local Memory / Spill Stores。Spill 一出现，优先减寄存器压力，不要先改算法故事。
4. Warp Stall Reason：long scoreboard（等内存）、short scoreboard（管道）、MIO、barrier、not selected。Decode 读 KV 几乎一定是 long scoreboard；这时 GQA / 量化 cache 比「提高 occupancy」对症。
5. Tensor Core 利用率、L1/L2 hit。MMA 没发出来，是 tile 形状 / dtype / alignment；不是 occupancy 开关。

Roofline 和 SOL 是同一句话：先定性墙，再动资源。面试如果一上来「我把 occupancy 从 40% 调到 70%」，评委会问「SOL 哪根柱子动了」。

Grid 太小是 serving decode 的常见坑：batch 小、query 长度 1，活跃 warp 填不满 GPU。FlashDecoding 沿 KV 切开，就是在造 occupancy。这和训练 prefill 大 GEMM 完全两副药。

## 追问

- **Occupancy 100% 一定最快？** 不一定。寄存器少可能意味着少做缓存、指令更多。有的核 30% occupancy 但 SOL 内存 85%，已经到顶。
- **Shared memory 加大为什么变慢？** 每 block 吃更多 SRAM，同时能住的 block 变少，occupancy 掉；如果这次加大是为了 tile 命中（FA），仍然可能净赚。要看 SOL，不要看单一百分比。
- **和 CUDA graph / 启动开销？** 小核 occupancy 再高也被 launch 淹没。Systems 上看到一串很短的 kernel，先融合或 graph，别调寄存器。
- **NCCL 的 occupancy 要盯吗？** 大消息 NCCL 是带宽墙；小消息是延迟。训练里优先看它是否和 GEMM 重叠，见 `nvidia-nccl-allreduce`。
