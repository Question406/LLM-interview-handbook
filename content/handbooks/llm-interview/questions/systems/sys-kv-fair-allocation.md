---
id: sys-kv-fair-allocation
section: systems
order: 24
level: A
title: 动态长度、多分支 sampling 的 KV Cache 如何分配，为什么要有 block / page、copy-on-write 和 preemption 策略？
quick: 连续预留会碎片化且无法高效共享 prefix。块级 page 分配允许动态增长、共享前缀和分支 copy-on-write；容量不足时在 recompute、swap、preempt 间权衡，并观测 KV OOM、尾延迟、被抢占率和吞吐。
tags:
  - KV Cache
  - PagedAttention
  - Scheduling
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

每条请求的生成长度未知，beam / Best-of-N 分支又会共享部分 prefix。若按最大长度连续分配，短请求造成浪费，长请求容易因碎片化失败。page/block table 让序列按需增长，并能引用计数共享 prefix。

分支开始写入共享 block 时使用 copy-on-write，避免彼此覆盖；内存紧张时选择暂停并重算、swap 到 host，或抢占低优先级请求。每种策略在 latency、PCIe 开销、吞吐与公平性上不同。

调度器不能只盯 GPU utilization。应按请求长度和 priority 看 KV OOM、fragmentation、preemption、recompute、P99 latency 与每完成请求 token，才能避免短请求或大 tenant 挤压其他流量。
