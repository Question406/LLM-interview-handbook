---
id: drustz-a344d2b9f62f86de9a
section: plans
order: 46
level: A
title: 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 11：AI System Design
quick: 作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 11：AI System Design
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

## Week 11：AI System Design

### 本周目标

把 LLM/AI infra 知识组织成 system design 答案。

### 必练题

1. LLM Inference API
2. Dynamic batching service
3. RAG system
4. Prompt playground
5. GPU job scheduler
6. Training data pipeline
7. Model evaluation platform
8. Distributed KV Store
9. Realtime chat / Slack-like system
10. Payment / idempotency system

### AI System Design 答题框架

```text
1. Requirements
   - functional
   - non-functional
   - scale
   - latency / throughput / cost / safety

2. API
   - request / response
   - streaming or non-streaming
   - idempotency key

3. Data model
   - request state
   - user/session/conversation
   - cache key
   - metrics/events

4. High-level architecture
   - gateway
   - scheduler
   - workers
   - storage
   - observability

5. Core flow
   - read path
   - write path
   - failure path

6. Scaling bottlenecks
   - GPU memory
   - queueing delay
   - hot keys
   - network bandwidth
   - storage IO

7. Reliability
   - retry
   - timeout
   - cancellation
   - checkpoint
   - rollback

8. Security / safety
   - auth
   - rate limit
   - abuse prevention
   - content safety
   - audit logs

9. Metrics
   - latency
   - throughput
   - GPU utilization
   - cache hit rate
   - error rate
   - quality / safety eval
```



### 本周输出物

`week11_ai_system_design/`

写 5 篇完整答案：

- `llm_inference_api.md`
- `dynamic_batching_service.md`
- `rag_system.md`
- `gpu_scheduler.md`
- `model_eval_platform.md`

### 判断是否过关

每道题能讲 35–45 分钟，并且不只是传统后端，而是能讲到 GPU / batching / cache / safety / metrics。

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
