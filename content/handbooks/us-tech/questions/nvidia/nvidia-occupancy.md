---
id: nvidia-occupancy
section: nvidia
order: 11
level: S
title: NVIDIA：CUDA occupancy、register 压力，Nsight 上看什么
quick: >-
  Occupancy 是一个 SM 上活跃 warp 数占硬件上限的比例，反映能用多少并行工作隐藏延迟。寄存器或共享内存用得多，能同时驻留的 warp
  就少，还可能出现寄存器 spill；诊断时先用 Nsight Systems 看 GPU 是否空闲，再用 Nsight Compute 看
  throughput、资源限制和等待原因。提高 occupancy 是否有收益，要看原来的瓶颈。
tags:
  - NVIDIA
  - CUDA
  - Occupancy
  - Nsight
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: CUDA C++ Programming Guide — Occupancy
    url: 'https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#occupancy'
    type: primary
  - title: Nsight Compute Profiling Guide
    url: 'https://docs.nvidia.com/nsight-compute/ProfilingGuide/index.html'
    type: primary
  - title: >-
      FlashAttention — Fast and Memory-Efficient Exact Attention with
      IO-Awareness
    url: 'https://arxiv.org/abs/2205.14135'
    type: primary
---

## 可以这样回答

Occupancy 决定一个 SM 上能同时保留多少个活跃 warp，能帮助隐藏延迟，但实际速度还取决于计算和访存。比如把每线程寄存器从 64 增到 128，能驻留的 warp 会变少；如果多用寄存器因此省了很多 HBM 访问，整体仍可能更快。判断时我会先看 GPU 有没有工作，再进 kernel 查资源和 throughput。

训练和推理里也会碰到这个问题：FlashAttention 的 occupancy 可能不高，TP 之后的小 kernel 也可能填不满 GPU。集合通信造成的空转见 `nvidia-nccl-allreduce`，这题关注 kernel 内部的执行。

## 技术备查

Occupancy 决定一个 SM 上能同时保留多少个活跃 warp，能帮助隐藏延迟，但实际速度还取决于计算和访存。比如把每线程寄存器从 64 增到 128，能驻留的 warp 会变少；如果多用寄存器因此省了很多 HBM 访问，整体仍可能更快。判断时我会先看 GPU 有没有工作，再进 kernel 查资源和 throughput。

训练和推理里也会碰到这个问题：FlashAttention 的 occupancy 可能不高，TP 之后的小 kernel 也可能填不满 GPU。集合通信造成的空转见 `nvidia-nccl-allreduce`，这题关注 kernel 内部的执行。

## Occupancy 和寄存器

一个 SM 能同时放的 warp 有上限（架构决定，例如 64）。Occupancy 等于活跃 warp 除以上限。能驻留多少 warp，要同时满足寄存器、共享内存和硬件槽位的限制：

- 每线程寄存器（A100/H100 一个 SM 大约 64K 个 32-bit 寄存器）；
- 每 block 共享内存；
- 每 SM 的 block / warp 槽位。

把寄存器算一遍就容易理解：64 个寄存器/线程 $\times$ 32 线程/warp $= 2048$ 寄存器/warp。$64\mathrm{K}/2048=32$ 个 warp，上限 64 时 theoretical occupancy 50%。再翻倍到 128 寄存器/线程，只剩 16 个 warp，25%。编译器还会 spill：寄存器不够就把变量放到 local memory（逻辑上每个线程一份，物理上走 HBM），延迟比寄存器差一截。这时即使 occupancy 看起来不低，也可能有大量 long scoreboard 等待，因为数据要从 spill 所在的内存读回来。

较高的 occupancy 提供更多可切换的 warp，能帮助隐藏指令和内存延迟。如果 kernel 已经是计算墙且流水线满，再加 warp 不会更快。如果瓶颈是 HBM 带宽，就应像 FlashAttention 那样减少访存；即使把 occupancy 提到 80%，也未必能突破带宽上限。FlashAttention 吃大量 SRAM，theoretical occupancy 往往一般，但 HBM 访问掉一个数量级，墙的位置变了，见 `nvidia-flash-attn`。

`__launch_bounds__`、少 live variable、拆核、用 Occupancy Calculator，都是在和寄存器 / 共享内存做交换。乱加 `__restrict__` 或盲目加大 block，可能把 spill 换来。

## Nsight 上看什么

先用 Nsight Systems 看 GPU 时间线。如果有大量空白，就查 launch、CPU、NCCL 或 dataloader；此时调整核内 occupancy 帮不上忙。如果 kernel 已经连续执行，再用 Nsight Compute 看内部瓶颈。

进入 kernel 后，我会按下面的顺序核对：

1. 先看 Speed of Light 里的 SM 与 Memory throughput。哪边先到 70% 以上，就先查那边的瓶颈；两边都低时，再查 occupancy、指令调度，或是否根本没用上 Tensor Core。
2. 再比较 Theoretical 和 Achieved Occupancy。理论值低，先查寄存器和 shared memory 预算；实测明显低于理论值，再查 barrier 等待、block 数不足，或 decode 单步 grid 太小。
3. 检查 Registers Per Thread、Local Memory 和 Spill Stores。有 spill 就先尝试降低寄存器压力，再测是否改善等待和 throughput。
4. 用 Warp Stall Reason 区分 long scoreboard 的内存等待、short scoreboard 的管道等待，以及 MIO、barrier、not selected。decode 读 KV 常主要等内存，这时优先比较 GQA 和 cache 量化。
5. 最后看 Tensor Core 利用率和 L1/L2 hit。MMA 没发出来时查 tile 形状、dtype、alignment，单调 occupancy 不能修复这些问题。

用 Roofline 或 SOL 分析时，都要先确认主要受计算还是内存限制，再调整资源。比如 occupancy 从 40% 提到 70%，还要检查 throughput 是否提高，才能说明这次调整有用。

Grid 太小是 serving decode 的常见坑：batch 小、query 长度 1，活跃 warp 填不满 GPU。FlashDecoding 沿 KV 切开，就是在造 occupancy。这与训练或 prefill 的大 GEMM 不同，调优时应分别测量。

## 追问

**Occupancy 100% 一定最快？**
不一定。少用寄存器可能减少缓存、增加指令。有的核 occupancy 只有 30%，SOL 内存 throughput 却已达 85%，此时主要受带宽限制。
**Shared memory 加大为什么变慢？**
因为每个 block 占用更多 SRAM，同一 SM 能驻留的 block 就变少，occupancy 随之下降。但像 FA 那样用更大 tile 减少访存，仍可能获得净收益，要结合 SOL 看。
**和 CUDA graph / 启动开销？**
小核可能主要耗在 launch。Systems 上若是一串很短的 kernel，先比较融合或 CUDA Graph 的效果，再调寄存器。
**NCCL 的 occupancy 要盯吗？**
大消息 NCCL 是带宽墙；小消息是延迟。训练里优先看它是否和 GEMM 重叠，见 `nvidia-nccl-allreduce`。
