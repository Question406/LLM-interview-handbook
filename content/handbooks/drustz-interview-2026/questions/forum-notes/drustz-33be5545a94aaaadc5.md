---
id: drustz-33be5545a94aaaadc5
section: forum-notes
order: 215
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Complexity Overview
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Complexity Overview
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
## Complexity Overview

| Method | Time | Space |
| --- | --- | --- |
| `add_user` | O(1) | O(1) |
| `follow` | O(1) | O(1) |
| `create_snapshot` | O(U + E) | O(U + E) |
| `is_following` | O(1) | O(1) |
| `get_following` | O(F) | O(F) |
| `get_followers` | O(F) | O(F) |
| `recommend` | O(F × G + C log K) | O(C) |

- **U** = Users
- **E** = Edges (total follows)
- **F** = Friends (of the specific user)
- **G** = Average friends per user
- **C** = Candidates found
- **K** = Top-K limit

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100180*)

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
