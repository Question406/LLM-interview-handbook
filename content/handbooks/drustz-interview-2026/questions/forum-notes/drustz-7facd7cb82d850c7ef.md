---
id: drustz-7facd7cb82d850c7ef
section: forum-notes
order: 334
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Problem Statement
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Problem Statement
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
## Problem Statement

You need to build a system that manages a block of computer memory. Your tool should work like `malloc()` and `free()` in C. It handles asking for memory (allocation) and giving it back (deallocation).

Your `MemoryAllocator` must:

- Start with a set total amount of memory.
- Give out unbroken (contiguous) blocks of memory.
- Take back memory when it is no longer needed.
- Fix gaps in memory (fragmentation).
- Report errors if a request is invalid or if there is no space left.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
