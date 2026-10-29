---
id: drustz-2709b350d7ca3b1df4
section: forum-notes
order: 359
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Helpful Tips
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Helpful Tips
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
## Helpful Tips

- **Avoid SQL Parsing:** Do not try to read a string like `SELECT * FROM`. Use function arguments instead.
- **Copy Data:** When inserting data, use `.copy()`. If you don't, changing the original dictionary later might mess up your database.
- **Check for None:** Your `where` and `order_by` arguments are optional. Make sure your code handles `None` without crashing.
- **Empty Results:** If no data matches the filter, return an empty list `[]`, not `None`.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
