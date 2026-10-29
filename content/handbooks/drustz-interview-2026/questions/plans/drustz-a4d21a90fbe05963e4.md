---
id: drustz-a4d21a90fbe05963e4
section: plans
order: 40
level: A
title: 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 5：Inference / Decoding / KV Cache
quick: >-
  作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 5：Inference / Decoding / KV
  Cache
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 作者复习计划与报告
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md
    type: primary
---
> 下文的个人经历、时间安排与复习状态属于原作者 DrustZ；可用作组织自己材料的参考。

## Week 5：Inference / Decoding / KV Cache

### 本周目标

进入 AI lab 高频核心：模型怎么服务用户。

### 必学概念

- Prefill
- Decode
- Autoregressive generation
- KV cache
- KV cache shape
- Greedy decoding
- Temperature
- Top-k / top-p
- Repetition penalty
- Stop token / stop sequence
- Streaming
- Latency vs throughput
- Memory bandwidth bottleneck
- Context length vs memory

### 你必须能回答的问题

1. Prefill 和 decode 的计算模式有什么不同？
2. KV cache 存 K/V，为什么不存 Q？
3. KV cache 的 shape 大概是什么？
4. context length 变长，显存为什么增长？
5. decode 为什么经常 memory-bound？
6. top-k 和 top-p 有什么区别？
7. repetition penalty 通常怎么改 logits？
8. streaming response 是怎么实现的？

### 小实现

- [ ] toy autoregressive decode loop
- [ ] greedy / top-k / top-p sampling
- [ ] repetition penalty
- [ ] stop sequence matcher
- [ ] KV cache append/read mock
- [ ] request state machine

### 本周输出物

`week5_inference_kv_cache.md`

必须包含：

- prefill vs decode 对比
- KV cache shape 图
- sampling 方法对比
- 一个 toy decode loop

### 判断是否过关

能回答：

> “为什么 batching 对 decode throughput 很重要？为什么不是所有 request 都适合简单 static batching？”

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
