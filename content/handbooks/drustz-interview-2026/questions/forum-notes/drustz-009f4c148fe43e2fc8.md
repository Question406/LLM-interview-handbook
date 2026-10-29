---
id: drustz-009f4c148fe43e2fc8
section: forum-notes
order: 197
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Worked Example
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Worked Example
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
## Worked Example

Suppose:

```text
t = 3, m = 2, h = 4, k = 2
```



One valid schedule is:

```python
[
    (0, 0, 0),
    (1, 0, 1),
    (2, 0, 2),
    (0, 1, 3),
    (1, 1, 0),
    (2, 1, 1),
    (0, 0, 2),
    (1, 0, 3),
]
```



Check the properties:

- every human appears exactly `2` times
- no human repeats the same task
- for task `0`, model counts evolve as `(1,0)`, then `(1,1)`, then `(2,1)` so the difference never exceeds `1`
- the same holds for tasks `1` and `2`

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
