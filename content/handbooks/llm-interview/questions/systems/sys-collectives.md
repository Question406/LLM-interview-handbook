---
id: sys-collectives
section: systems
order: 13
level: A
title: Ring AllReduce、ReduceScatter + AllGather 有什么关系？
quick: >-
  Ring AllReduce 通常可分解为 reduce-scatter + all-gather 两个阶段：先每个 rank
  得到一片完整规约结果，再把所有片广播拼回完整 tensor。
tags:
  - NCCL
  - Distributed
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Ring AllReduce 通常可分解为 reduce-scatter + all-gather 两个阶段：先每个 rank 得到一片完整规约结果，再把所有片广播拼回完整 tensor。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>Ring 将 tensor 切成 N chunks，沿环发送/规约 N−1 步完成 reduce-scatter，再 N−1 步 all-gather。大消息下带宽利用率高，但 latency 与 rank 数/拓扑有关。</p><p>ZeRO/FSDP 常直接使用 reduce-scatter gradients，因为每个 rank 最终只需保留自己的 shard，不需要再 all-gather完整 gradient。</p><p>NCCL bottleneck 可能来自 PCIe/NVLink/IB 拓扑不匹配、跨 NUMA、message size 太小、通信与计算 overlap 不足。</p></div>
