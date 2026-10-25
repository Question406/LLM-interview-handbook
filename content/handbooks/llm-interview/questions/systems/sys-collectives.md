---
id: sys-collectives
section: systems
order: 13
level: A
title: Ring AllReduce、ReduceScatter + AllGather 有什么关系？
quick: "Ring AllReduce 可以拆成 reduce-scatter 和 all-gather：先让各 rank 拿到自己那一片的完整规约，再收齐所有片。ZeRO/FSDP 只需要本 rank 的 gradient shard 时，梯度归约做到 reduce-scatter 就够，参数再按需 all-gather。"
tags:
  - NCCL
  - Distributed
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

Ring AllReduce 可以先做 reduce-scatter，让每个 rank 拿到自己那一片的完整规约，再 all-gather 拼回全量。理解时可以先问每个 rank 最终需要什么：普通 DP 需要完整梯度，而 ZeRO/FSDP 可能只需要自己的 gradient shard，做到第一段就能停，见 `sys-zero`。

$N$ 个 rank 把 tensor 切成 $N$ chunks，沿环每次传一块：

1. **Reduce-scatter**：$N-1$ 步，每步对自己收到的 chunk 做规约再传出。结束时 rank $i$ 持有第 $i$ 片的**完整和**。
2. **All-gather**：再 $N-1$ 步，把各片广播拼回完整 tensor。

大消息下带宽利用率高（每步都在传数据），但步数随 $N$ 线性涨，latency 受 rank 数和环拓扑影响。小消息更吃延迟，NCCL 会换 tree 等算法，不要背「永远 ring」。

普通 DP 要 AllReduce 出完整梯度再让每个 rank 本地更新。ZeRO-2/3 的梯度本就按 DP rank 分片，reduce-scatter 之后 rank $i$ 只需更新自己那片，**不必**再 all-gather 完整梯度。参数若也分片（ZeRO-3 / FSDP），forward 前再 all-gather 当前层权。通信模式从「每次完整 AllReduce」变成「RS + 按需 AG」，显存降、通信次数升。

NCCL 慢可能来自 PCIe / NVLink / IB 拓扑不匹配、跨 NUMA、message 太小、通信与计算 overlap 不足。死锁则是有的 rank 没进同一 collective，见 `stepfun-gpu-deadlock`。画出两段共 $2(N-1)$ 步，再标明谁需要全量，就能判断哪里需要 AG、哪里停在 RS。

## 追问

**AllReduce 的带宽怎么估？**
Ring 下每 rank 传约 $2\frac{N-1}{N}M$ 字节（$M$ 为张量大小），接近 $2M$，与 $N$ 弱相关。步数仍是 $2(N-1)$。
**FSDP 为什么是 RS + AG？**
梯度 RS 回自己的 shard；下一层 forward 再 AG 参数。和 ZeRO-3 同构。
**小 tensor 也用 ring 吗？**
不一定。延迟占主导时 tree 更合适，NCCL 会按 size 选。
**和 TP 的 AllReduce 是一回事吗？**
集合原语相同，切的轴不同：TP 常在层内激活/权，DP/ZeRO 在副本间梯度。
**overlap 不足怎么表现？**
计算结束通信还在飞，MFU 掉、GPU 空等。大消息 ring 更要和 GEMM 叠，否则两段 $N-1$ 步全暴露在关键路径上。
