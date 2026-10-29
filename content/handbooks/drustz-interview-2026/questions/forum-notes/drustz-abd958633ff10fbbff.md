---
id: drustz-abd958633ff10fbbff
section: forum-notes
order: 33
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 2: Ranking Spenders'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 2: Ranking Spenders'
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
## Level 2: Ranking Spenders

### Goal

The bank wants to know who spends the most money. You need to rank accounts based on how much money goes out.

### New Function

#### top_spenders

```text
top_spenders(self, timestamp: int, n: int) -> list[str]
```



- **Action:** Find the top `n` accounts that have sent the most money out.
- **Outgoing Money Includes:**

Money transferred to others.
- Money paid/withdrawn (added in Level 3).
- **Sorting Rules:**

Sort by total outgoing money (Highest to Lowest).
- If two accounts spent the same amount, sort them alphabetically by `account_id` (A to Z).
- **Returns:** A list of strings in this format:
`["id1(spent_amount)", "id2(spent_amount)"]`
- **Note:** If there are fewer than `n` accounts, just return all of them. Do not include Cashback in these totals.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
