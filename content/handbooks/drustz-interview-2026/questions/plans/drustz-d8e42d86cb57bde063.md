---
id: drustz-d8e42d86cb57bde063
section: plans
order: 63
level: A
title: 3–4 个月高强度 Frontier AI Lab 面试学习规划 · 10.1 Transformer Knowledge Map
quick: 作者文档章节 · 3–4 个月高强度 Frontier AI Lab 面试学习规划 · 10.1 Transformer Knowledge Map
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

## 10.1 Transformer Knowledge Map

```text
Token IDs
  ↓
Embedding + Position / RoPE
  ↓
Transformer Block × N
  ├── Norm
  ├── QKV Projection
  ├── Attention Scores
  ├── Causal Mask
  ├── Softmax
  ├── Weighted Sum V
  ├── Output Projection
  ├── Residual
  ├── MLP
  └── Residual
  ↓
Logits
  ↓
Loss or Sampling
```



必须会讲：

- training 时 logits 对所有 position 并行计算
- inference decode 时每次只生成下一个 token
- KV cache 缓存历史 K/V
- attention complexity 与 sequence length 有关

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/frontier_ai_lab_3_4_month_study_plan.md)。作者整理资料；许可和第三方来源范围见阅读指南。
