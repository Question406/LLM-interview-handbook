---
id: sys-mixed-traffic-scheduler
section: systems
order: 22
level: S
title: 长 prompt 把聊天请求 TTFT 打爆时，continuous batching 与 chunked prefill 怎么设计 / 调参？
quick: Prefill 和 decode 争同一 GPU token budget。用 chunked prefill 把长输入切块并与 decode 交错，设置 max batched tokens、partial-prefill 上限、抢占与防饥饿；按流量切片验收 P50/P95 TTFT、TPOT 与 goodput。
tags:
  - Scheduling
  - Continuous Batching
  - TTFT
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: vLLM Scheduler Configuration
    url: https://docs.vllm.ai/en/stable/api/vllm/config/scheduler/
    type: primary
---

长 prompt 的 prefill 计算密集且会占用大量 batch budget；短聊天请求的 decode 则对每步调度和 KV residency 敏感。若任由长 prefill 连续运行，短请求排队会导致 TTFT 长尾爆炸。

chunked prefill 将长请求拆块，在 decode step 间穿插执行。关键旋钮包括每轮 max batched tokens、chunk 大小、等待 partial prefill 的数量、优先级、抢占策略和等待上限；调小 chunk 可改善交互延迟，但会增加调度开销。

不能只追平均 throughput。按输入长度、输出长度、tenant、优先级分别报告 TTFT、TPOT、queue delay、preemption 和 goodput，防止一个流量类受益而另一个被饿死。
