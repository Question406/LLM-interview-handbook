---
id: drustz-721fe5d2f8bccb74dc
section: forum-notes
order: 75
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Mistakes to Avoid
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Mistakes to Avoid
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
## Mistakes to Avoid

- **Unlimited Queues**: Never let a queue grow forever; it will crash the server.
- **One Queue for Everyone**: Free users will block Paid users. Use separate queues.
- **Ignoring Cold Start**: Forgetting that new GPUs take 5 minutes to start.
- **Too Many Retries**: If the system is down, retrying continuously makes it harder to recover.
- **No Backpressure**: You must be able to tell users "Stop" when the system is full.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
