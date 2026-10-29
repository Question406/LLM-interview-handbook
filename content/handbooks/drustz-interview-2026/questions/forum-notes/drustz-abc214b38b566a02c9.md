---
id: drustz-abc214b38b566a02c9
section: forum-notes
order: 252
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Step 1: What We Need'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Step 1: What We Need'
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
## Step 1: What We Need

### Basic Features

- **Solve puzzles** — Take a board and a dictionary, then find a valid set of words.
- **Handle rules** — Words must fit the length of the slot and share letters where they cross.
- **Return solution** — Show the user the completed puzzle.

### What We Don't Need

- Making new puzzles from scratch.
- Understanding clues (we ignore the meaning of clues).
- Finding every possible answer (finding one is enough).
- User interface (UI) for editing.

### System Goals

| Requirement | Target | Notes |
| --- | --- | --- |
| Board size | ~50×50 | Medium-sized puzzle |
| Word slots | ~100 slots | Each needs a word from the list |
| Dictionary | ~1 million words | Standard English dictionary |
| Latency | Minutes acceptable | This is a slow job, not instant |
| Reliability | Must find solution | If an answer exists, we must find it |

The interviewer will likely say the board is 50×50. This is big enough to ensure that a simple brute-force approach on one computer will fail. This forces you to design a distributed system.

### Why One Computer Fails

**The Math:**

- 100 slots to fill.
- About 1,000 words fit each slot length.
- Total combinations: $1000^{100} = 10^{300}$.
- Even with shortcuts, this is too big for one machine.
**The Insight:** Logic cuts down the list of choices, but you still need many computers working together to search through the remaining options.

**Common mistake:** Do not waste time optimizing the code for one computer. Prove it won't work, then start designing the distributed system.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
