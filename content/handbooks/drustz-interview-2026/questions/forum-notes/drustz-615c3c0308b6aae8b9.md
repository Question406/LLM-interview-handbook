---
id: drustz-615c3c0308b6aae8b9
section: forum-notes
order: 98
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Critical Rules
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Critical Rules
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
## Critical Rules

### Name Uniqueness

- "PASTA", "Pasta", and "pasta" are the same name.
- Always ignore case when checking for duplicates.
- Store the name exactly as the user typed it.

### Rollback Conflicts

- When restoring an old version, check its name.
- If that old name is now used by a **different** recipe, the rollback must fail.
- A recipe never conflicts with its own history.

### Version Numbers

- Start counting at 1.
- Every edit or rollback adds +1 to the version number.
- Never reset or reuse numbers.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
