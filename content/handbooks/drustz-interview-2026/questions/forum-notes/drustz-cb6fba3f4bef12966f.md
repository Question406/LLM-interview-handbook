---
id: drustz-cb6fba3f4bef12966f
section: forum-notes
order: 194
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Problem Statement
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Problem Statement
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## Problem Statement

You are given:

- `t` tasks, indexed `0..t-1`
- `m` models, indexed `0..m-1`
- `h` human labelers, indexed `0..h-1`
- a target `k`
Return a scheduling, represented as a list of tuples:

```python
(task, model, human)
```



Each tuple means:

- human `human` works on task `task`
- that assignment is paired with model `model`
Your schedule must satisfy:

- Every human labeler participates in at least `k` assignments total.
- Every `(task, human)` pair appears at most once.
- For every task `x`, and for every prefix of the schedule, the counts across models stay balanced:

```text
max_i count_prefix(x, model=i) - min_i count_prefix(x, model=i) <= 1
```



- For every task `x`, and for every prefix of the schedule, the counts across humans also stay balanced:

```text
max_j count_prefix(x, human=j) - min_j count_prefix(x, human=j) <= 1
```



If no valid schedule exists, return failure in whatever form your language uses (`None`, empty list, exception, etc.).

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
