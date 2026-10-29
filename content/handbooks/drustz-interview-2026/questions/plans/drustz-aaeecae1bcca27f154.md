---
id: drustz-aaeecae1bcca27f154
section: plans
order: 65
level: A
title: 3–4 个月高强度 Frontier AI Lab 面试学习规划 · 10.3 Inference Knowledge Map
quick: 作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · 10.3 Inference Knowledge Map
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

## 10.3 Inference Knowledge Map

```text
User request
  ↓
Tokenization
  ↓
Queue / scheduler
  ↓
Prefill
  ↓
KV cache creation
  ↓
Decode loop
  ├── select active batch
  ├── model forward one token
  ├── logits processing
  ├── sampling
  ├── KV cache update
  ├── stop condition
  └── stream token
  ↓
Final response
```



必须会讲：

- prefill 更像大矩阵计算
- decode 更容易受 memory bandwidth 和 batch utilization 限制
- continuous batching 提升 GPU utilization
- prefix cache 降低重复 prompt 的 prefill cost

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
