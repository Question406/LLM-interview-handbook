---
id: drustz-b02af1bb1e2c4281de
section: forum-notes
order: 89
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Additional Design Details
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Additional Design Details
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
## Additional Design Details

### API Design

We use **Cursor-based Pagination**.

- Instead of saying "Page 1, Page 2," we say "Give me 50 items starting after this specific ID."
- This is faster for databases and works better when data is constantly being added.

### UI Layout

- **Left:** Library/History sidebar.
- **Center:** The big Editor.
- **Right:** Configuration (Temperature, Model selection).
- **Bottom:** The output window (streaming text).

### Security

- **Prompt Injection:** Warn users if a shared prompt looks dangerous.
- **Data Privacy:** Allow users to delete their data fully (GDPR).
- **Access:** Use JWT tokens for login.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
