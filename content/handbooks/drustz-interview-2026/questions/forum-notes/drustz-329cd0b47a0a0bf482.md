---
id: drustz-329cd0b47a0a0bf482
section: forum-notes
order: 214
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Follow-Up Questions
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Follow-Up Questions
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
## Follow-Up Questions

### Common Interview Topics

- **Immutability:** How do you make sure snapshots don't break?

**Deep copy** is the easiest way.
- For very big systems, copying everything is too slow. You might use **Copy-on-Write** or store data with version timestamps.
- **Scaling:** What if there are millions of users?

Full copies take too much memory.
- Store only the **deltas** (the changes) between snapshots.
- Or, store edges with a time range, like `[created_at, deleted_at]`.
- **Better Recommendations:**

Give more points for recent interactions.
- Look at "friends of friends of friends" (2nd degree connections).
- **Concurrency:** Handling many users at once?

Use **read-write locks**. Many people can read snapshots at the same time, but only one person can add a follow at a time.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
