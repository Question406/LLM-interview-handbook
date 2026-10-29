---
id: drustz-68542b0cfda6e4e615
section: plans
order: 41
level: A
title: >-
  3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 6：Parallelism / Distributed Training /
  Serving Infra
quick: >-
  作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · Week 6：Parallelism / Distributed
  Training / Serving Infra
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

## Week 6：Parallelism / Distributed Training / Serving Infra

### 本周目标

掌握大模型训练和推理里最常见的并行方式，尤其是 TP 和 FSDP。

### 必学概念

- Data Parallel
- Tensor Parallel
- Column Parallel Linear
- Row Parallel Linear
- Pipeline Parallel
- Sequence Parallel
- FSDP
- ZeRO-1 / ZeRO-2 / ZeRO-3
- All-reduce
- All-gather
- Reduce-scatter
- Activation checkpointing
- Communication/computation overlap
- GPU memory breakdown

### 你必须能回答的问题

1. Data parallel 切的是什么？为什么需要 all-reduce gradients？
2. Column parallel linear 的 forward 输出如何拼？backward 需要什么通信？
3. Row parallel linear 的 forward 为什么需要 all-reduce？
4. FSDP 和普通 data parallel 的区别是什么？
5. ZeRO-1/2/3 分别 shard 什么？
6. activation checkpointing 用计算换什么？
7. TP、PP、FSDP 在 training 和 inference 中用途有何不同？
8. 通信瓶颈出现在哪里？

### 小实现

- [ ] toy data parallel matmul
- [ ] toy column parallel linear
- [ ] toy row parallel linear
- [ ] FSDP all-gather / reduce-scatter mock
- [ ] 参数量和显存估算表

### 本周输出物

`week6_parallelism_fsdp_tp.md`

必须包含：

- DP / TP / PP / FSDP 对比
- Column TP / Row TP 图解
- FSDP forward/backward 通信图
- memory accounting example

### 判断是否过关

别人问 column TP / row TP backward，你不能只说 “all-reduce / all-gather”，你要能说清楚为什么。

---

# 5. Phase 2：知识转实现，Week 7–10

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
