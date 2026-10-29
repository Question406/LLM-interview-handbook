---
id: drustz-fd0bd32dc136689b61
section: forum-notes
order: 195
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Build Any Valid Schedule'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Build Any Valid Schedule'
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
## Part 1: Build Any Valid Schedule

Ignore the prefix-balance constraints for now. Just return any schedule such that:

- each human appears at least `k` times
- each human works on a given task at most once

### Key Observation

Because each human can touch a task at most once, a human can do at most `t` assignments total. Therefore:

```text
k > t  =>  impossible
```



That is the main feasibility condition for Part 1.

### Simple Construction

If `k <= t` and `m >= 1`, assign each human to `k` distinct tasks, for example:

```python
for human in range(h):
    for offset in range(k):
        task = (human + offset) % t
        model = 0
        schedule.append((task, model, human))
```



This is already enough for the easy part.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
