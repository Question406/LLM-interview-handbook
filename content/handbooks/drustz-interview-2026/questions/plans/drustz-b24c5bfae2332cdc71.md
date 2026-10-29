---
id: drustz-b24c5bfae2332cdc71
section: plans
order: 43
level: A
title: 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 8：LLM Serving Coding
quick: 作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 8：LLM Serving Coding
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

## Week 8：LLM Serving Coding

### 本周目标

把 Week 5 的 inference 知识变成代码实现。

### 高频题

- Dynamic Batch Inference Engine
- Continuous Batching Scheduler
- Request Queue / Active Batch
- Token Budget Manager
- Rate Limiter
- Prefix Cache / Radix Cache
- Repetition Penalty
- Stop Sequence Handling

### Dynamic Batching 的核心状态

你要会设计这些对象：

```text
Request:
    id
    prompt_tokens
    generated_tokens
    max_new_tokens
    stop_tokens
    status
    kv_cache_handle

Scheduler:
    waiting_queue
    active_batch
    completed
    max_batch_size
    step()
```



### 关键 edge cases

- request 一开始就超过 max length
- stop token 出现在 batch 中某个 request
- stop sequence 跨 token 边界
- 某个 request 结束后 batch 空槽如何补位
- timeout / cancellation
- priority request
- max batch tokens vs max batch size
- prefill request 和 decode request 是否分队列

### 本周时间安排

| Day | 任务 |
|---|---|
| Day 1 | 写最小 decode loop |
| Day 2 | 加 request state + stop token |
| Day 3 | 加 dynamic batching slot reuse |
| Day 4 | 加 stop sequence / timeout |
| Day 5 | 写 rate limiter / token budget manager |
| Day 6 | 写 radix cache insert / longest prefix |
| Day 7 | 75 分钟 Dynamic Batch mock |

### 本周输出物

`week8_llm_serving_engine/`

必须包含：

- dynamic_batch_engine.py
- tests.py
- README.md：设计说明和 follow-ups

### 判断是否过关

能完整讲：

```text
waiting requests → prefill → active decode batch → token generation → finished cleanup → slot refill → streaming output
```



---

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
