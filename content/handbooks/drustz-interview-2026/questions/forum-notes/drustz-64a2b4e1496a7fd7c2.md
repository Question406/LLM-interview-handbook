---
id: drustz-64a2b4e1496a7fd7c2
section: forum-notes
order: 343
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · The Challenge
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · The Challenge
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
## The Challenge

You need to build a permanent key-value store. This store must be able to save data to a file system and read it back later. You will get a "mock" (fake) file system and some tools to turn numbers and strings into bytes.

The main difficulty is inventing your own format to save dictionaries. You **cannot** use easy tools like JSON or pickle. Your format must handle strings that contain strange characters.

**Important Context:**

- You get a fake file system, not a real one.
- You get helper functions to change integers and strings into bytes.
- **No JSON or pickle allowed.**
- Keys and values can have **any characters** (like new lines, emojis, or commas).
- You must be able to load the data back exactly as it was saved.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
