---
id: drustz-1e48cdde1bf74646cb
section: plans
order: 45
level: A
title: 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 10：Concurrency / Parallelism Coding
quick: >-
  作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 10：Concurrency / Parallelism
  Coding
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

## Week 10：Concurrency / Parallelism Coding

### 本周目标

把分布式和并发题变成可以写的代码。

### 高频题

- Multithread sorting
- Concurrent job scheduler
- Worker heap scheduling
- Producer-consumer queue
- Thread pool
- Web crawler single-thread → multi-thread
- File dedup parallel version
- Distributed matrix multiplication mock
- DP / FSDP toy implementation

### 本周时间安排

| Day | 任务 |
|---|---|
| Day 1 | Multithread merge sort |
| Day 2 | Thread pool + task scheduler |
| Day 3 | Heap worker scheduling |
| Day 4 | Web crawler multi-thread |
| Day 5 | File dedup parallel hashing |
| Day 6 | DP / FSDP toy matmul |
| Day 7 | xAI-style 45 分钟 mock |

### 本周输出物

`week10_concurrency_parallelism/`

必须包含：

- parallel_sort.py
- task_scheduler.py
- crawler_multithread.py
- distributed_matmul.py

### 判断是否过关

你能在 45 分钟内写出多线程排序的核心逻辑，并能解释：

- 如何 split
- 如何 merge
- thread 数怎么选
- GIL 对 Python CPU-bound 代码有什么影响
- 什么时候用 multiprocessing

---

# 6. Phase 3：系统设计与项目表达，Week 11–12

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
