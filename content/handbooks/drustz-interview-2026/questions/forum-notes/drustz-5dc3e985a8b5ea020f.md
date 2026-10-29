---
id: drustz-5dc3e985a8b5ea020f
section: forum-notes
order: 30
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Big O Analysis
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Big O Analysis
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
## Big O Analysis

Here is how efficient the solution is:

| Operation | Time Complexity | Space Complexity |
| --- | --- | --- |
| addTask | O(1) | O(1) |
| updateTask | O(1) | O(1) |
| getTask | O(1) | O(1) |
| searchTasks | O(T log T) | O(T) |
| listTasksSorted | O(T log T) | O(T) |
| addUser | O(1) | O(1) |
| assignTask | O(A) | O(1) |
| getUserTasks | O(A log A) | O(A) |
| completeTask | O(A log A) | O(A) |
| getOverdueAssignments | O(A log A) | O(A) |

**Definitions:**

- **T** = Total number of tasks.
- **A** = Number of assignments for a specific user.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100097*)

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
