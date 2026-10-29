---
id: drustz-716ceb6a1b2fc3e4b0
section: agent-core
order: 32
level: A
title: 06 · Evaluation 与 Security · 5. 从事故生成 eval ⭐⭐⭐
quick: 作者文档章节 · 06 · Evaluation 与 Security · 5. 从事故生成 eval ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/06_eval_security.md
    type: primary
---
## 5. 从事故生成 eval ⭐⭐⭐

1. 去 secret，固定最小可复现 environment。
2. 保留触发条件和预期 domain state，不把错误输出当答案。
3. 写 deterministic regression grader。
4. 加邻近变体，防只修单例。
5. 进入 held-out registry；训练数据与 held-out 分离。
6. offline → shadow → canary → rollout，任何阶段可 rollback。

> 高分句：每个 production incident 都应该变成一条带邻近变体的 held-out regression eval，而不是只修单例。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/06_eval_security.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/06_eval_security.md)。作者整理资料；许可和第三方来源范围见阅读指南。
