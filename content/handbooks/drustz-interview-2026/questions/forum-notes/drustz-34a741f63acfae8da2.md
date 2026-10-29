---
id: drustz-34a741f63acfae8da2
section: forum-notes
order: 300
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Project Requirements
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Project Requirements
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
## Project Requirements

You need to design a Webhook delivery system that can handle a massive amount of traffic. This system allows users to register a "callback URL." When a specific event happens, the system must send an HTTP POST request to that URL.

**Key constraints:**

- **Scale:** The system must handle 1 billion events every day.
- **Reliability:** It must deliver messages successfully and retry if the delivery fails.
- **Features:** It needs security, monitoring (observability), and a way to handle errors.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
