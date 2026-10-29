---
id: drustz-d1b3cdf63790ac6781
section: plans
order: 66
level: A
title: 3–4 个月高强度 Frontier AI Lab 面试学习规划 · 10.4 Parallelism Knowledge Map
quick: 作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · 10.4 Parallelism Knowledge Map
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

## 10.4 Parallelism Knowledge Map

```text
Large model too big / too slow
  ↓
Data Parallel: replicate model, split data
  ↓
Tensor Parallel: split matrix inside layer
  ├── Column Parallel
  └── Row Parallel
  ↓
Pipeline Parallel: split layers
  ↓
FSDP / ZeRO: shard params/grads/optimizer states
  ↓
Hybrid 3D Parallelism
```



必须会讲：

- DP 需要 gradient all-reduce
- TP 需要 layer 内通信
- PP 有 pipeline bubble
- FSDP 用通信换显存
- ZeRO 分阶段 shard optimizer / grad / param

---

# 11. Mock Interview 评分表

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
