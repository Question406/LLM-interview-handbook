---
id: drustz-cc22fc8ab93688fd96
section: agent-core
order: 22
level: A
title: 05 · Reliability 与 Failure Recovery · 1. 七类 failure taxonomy ⭐⭐⭐
quick: 作者文档章节 · 05 · Reliability 与 Failure Recovery · 1. 七类 failure taxonomy ⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/05_reliability.md
    type: primary
---
## 1. 七类 failure taxonomy ⭐⭐⭐

| # | 类别 | 典型失败 |
|---|---|---|
| 1 | Specification | 目标/约束/完成条件缺失或冲突 |
| 2 | Model decision | 选错工具、参数、计划或事实 |
| 3 | Tool/runtime | timeout、429、schema drift、坏结果、partial side effect |
| 4 | Coordination | 重复任务、handoff 丢信息、共享 state 冲突 |
| 5 | Verification | grader 漏洞、模型自评、错误 source、测试不覆盖 |
| 6 | Security/authority | 注入、越权、secret 泄露、confused deputy |
| 7 | Operations | worker crash、stale result、queue backlog、成本爆炸 |

> 高分句：「agent 出错了」不是一个 failure mode——先分类到七类之一，才能谈 detection 和 recovery。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/05_reliability.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/05_reliability.md)。作者整理资料；许可和第三方来源范围见阅读指南。
