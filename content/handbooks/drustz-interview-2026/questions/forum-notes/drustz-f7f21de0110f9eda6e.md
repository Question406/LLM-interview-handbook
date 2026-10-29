---
id: drustz-f7f21de0110f9eda6e
section: forum-notes
order: 36
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Special Rules & Edge Cases
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Special Rules & Edge Cases
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Special Rules & Edge Cases

### Recreating an Account

- If Account B is merged into Account A, Account B is deleted.
- You are allowed to create a **new** Account B later.
- This new Account B starts with &#36;0. It does not have the history of the old Account B (because that history moved to Account A).

### History Checks

- Imagine Account B merged into Account A at time `T`.
- If you ask for Account B's balance **before** time `T`: You get the old balance.
- If you ask for Account B's balance **after** time `T`: You get `None` (unless you created a new Account B).

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
