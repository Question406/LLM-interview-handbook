---
id: drustz-6ffd544f7b8d718fe1
section: forum-notes
order: 102
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · The Problem
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · The Problem
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
## The Problem

You are given a Python code for an in-memory LRU (Least Recently Used) cache. The code works, but there is a mistake in how it creates keys.

The error happens when the cache tries to handle variable arguments (`*args`) and keyword arguments (`**kwargs`).

Your task is to:

- **Read** the current code and see how it works.
- **Find the mistake** in the key creation step.
- **Fix the code** so it handles `*args` and `**kwargs` correctly.

### What You Need to Do

Your solution must:

- **Find the error** — Understand why `*args` and `**kwargs` break the current key maker.
- **Make keys hashable** — Change arguments into a format that can be used as dictionary keys.
- **Handle all arguments** — Work correctly with both `*args` and `**kwargs`.
- **Keep the cache accurate** — Ensure the same inputs always create the exact same key.

### Helpful Tips

- **Python Knowledge**: You need to know:

How `*args` and `**kwargs` work in Python.
- Which data types work as dictionary keys (hashable) and which do not.
- How to change arguments into a hashable format.
- **Hints**:

Remember that keyword arguments can be in any order. For example, `func(a=1, b=2)` is the same as `func(b=2, a=1)`.
- Think about changing unhashable types (like lists or dicts) into hashable types (like tuples or frozensets).
- Check Python's `functools` library for ideas.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
