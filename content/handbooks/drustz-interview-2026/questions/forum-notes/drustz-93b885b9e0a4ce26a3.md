---
id: drustz-93b885b9e0a4ce26a3
section: forum-notes
order: 232
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Complexity
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Complexity
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
## Complexity

For `m` queries, `n` training examples, and feature dimension `d`:

- **Time:** `O(mnd)` for the matrix multiply
- **Space:** `O(mn)` for the full distance or logit matrix
If `m * n` is too large to materialize, process `X_query` in chunks.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
