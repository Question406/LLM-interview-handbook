---
id: drustz-da63e4d4fd60598a0f
section: forum-notes
order: 358
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 6: Optimization Discussion'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 6: Optimization Discussion'
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
## Part 6: Optimization Discussion

**Note:** You usually discuss this part without writing code.

The interviewer might ask: "How can we make these queries faster?" You should discuss **Indexing**.

### Key Concepts

- **Inverted Index (For exact matches):**

This is like the index at the back of a book.
- Structure: `{column_name: {value: [list_of_row_indices]}}`.
- Example: If you look for "Alice", the index tells you exactly which row she is in.
- Benefit: Improves speed from O(n) to O(1).
- **B-Tree Index (For ranges):**

This keeps data sorted.
- It is great for queries using `>`, `<`, `>=`, or `<=`.
- **Composite Index:**

This is an index that combines two columns (like `age` and `name`) to speed up queries that check both.
- **Trade-offs:**

Indexes make **reading** (querying) faster.
- Indexes make **writing** (inserting) slower because you must update the index every time you add data.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
