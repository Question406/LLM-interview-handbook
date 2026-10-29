---
id: drustz-c5d04db6224f7dff06
section: forum-notes
order: 199
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Why The Construction Is Correct
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Why The Construction Is Correct
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
## Why The Construction Is Correct

### 1. Each human gets at least `k` assignments

There are exactly `k` rounds, and each human receives exactly one assignment per round. So each human appears exactly `k` times.

### 2. No human repeats the same task

For a fixed human `u`, the assigned tasks are:

```text
(u + 0) mod t,
(u + 1) mod t,
...,
(u + k - 1) mod t
```



These are all distinct when `k <= t`.

### 3. Model counts stay balanced for every task

Fix any task `x`. Each time `x` appears, we assign the next model in round-robin order:

```text
0, 1, 2, ..., m-1, 0, 1, ...
```



After any number of occurrences of task `x`, each model has been used either:

- `floor(c / m)` times, or
- `ceil(c / m)` times
where `c` is the number of times task `x` has appeared so far.

Therefore the difference between the largest and smallest model count is always at most `1`.

### 4. The schedule is minimal in length

Every tuple increases the total assignment count of exactly one human by `1`. Since each of the `h` humans must reach at least `k`, any valid schedule needs at least:

```text
h * k
```



assignments.

Our construction uses exactly `h * k`, so it is optimal in schedule length.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
