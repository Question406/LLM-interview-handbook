---
id: drustz-c969e8ebfc4fc8e636
section: forum-notes
order: 253
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Step 2: Data Structures'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Step 2: Data Structures'
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
## Step 2: Data Structures

### Main Objects

```text
Puzzle
├── id: UUID
├── width: integer
├── height: integer
├── slots: Slot[]
└── status: "pending" | "solving" | "solved" | "failed"

Slot
├── id: integer
├── start_row: integer
├── start_col: integer
├── direction: "across" | "down"
├── length: integer
├── clue: string | null               // Metadata, we ignore this
└── assigned_word: string | null

Dictionary
├── words: string[]
└── by_length: Map<integer, string[]>  // Grouped by word length

SearchState
├── id: UUID
├── puzzle_id: UUID
├── assignments: Map<slot_id, word>    // Current progress
├── remaining_slots: slot_id[]         // Empty slots
├── depth: integer                     // How deep we are in the tree
└── parent_state_id: UUID | null       // To go back if stuck

Task
├── id: UUID
├── puzzle_id: UUID
├── state_id: UUID
├── priority: integer
├── status: "pending" | "running" | "completed" | "dead_end"
└── assigned_worker: string | null
```



### Why We Designed It This Way

**Why track SearchState separately?**

- It lets us give work to different computers. Each state is a starting point for a worker.
- If a worker crashes, we can pick up where it left off.
- It lets us split big tasks into smaller ones.
**Why index the dictionary by length?**

- Slots have specific lengths. We only care about words that match that length.
- This shrinks the list of choices from 1 million to about 1,000–10,000 per slot.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
