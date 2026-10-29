---
id: drustz-ef58269ce7bf4f9fa6
section: forum-notes
order: 312
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Problem Description
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Problem Description
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
## Problem Description

You need to build a type system for a simple programming language. This language has four main features:

- **Primitives**: Basic types like `int`, `float`, and `str`.
- **Generics**: Placeholders usually written as uppercase letters (e.g., `T`, `T1`, `S`).
- **Tuples**: Lists of types inside brackets. These can hold primitives, generics, or other tuples.

*Examples:* `[int, T1, str]` or `[int, [str, T1]]`.
- **Functions**: These have a list of input parameters and one return type.

*Syntax:* `[input1, input2] -> output`
- *Example:* `[int, T1] -> [str, T1]`
Your goal is to write two classes: `Node` and `Function`.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
