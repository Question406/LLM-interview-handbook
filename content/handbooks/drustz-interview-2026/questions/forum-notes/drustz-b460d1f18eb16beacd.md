---
id: drustz-b460d1f18eb16beacd
section: forum-notes
order: 314
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Task 1: Converting to String'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Task 1: Converting to String'
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
## Task 1: Converting to String

You must write the `__str__()` method for both classes.

### Node Format

- **Primitives/Generics**: Return the name exactly as it is.

*Example:* `int` becomes `"int"`.
- **Tuples**: Return the types separated by commas, inside brackets.

*Example:* `[int, float]` becomes `"[int,float]"`.
- *Nested Example:* `[int, [str, T1]]` becomes `"[int,[str,T1]]"`.

### Function Format

- Format: `(param1,param2) -> returnType`
- *Example:* If inputs are `[int, T1]` and return type is `[T1, str]`, the string is `"(int,T1) -> [T1,str]"`.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
