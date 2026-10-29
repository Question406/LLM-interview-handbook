---
id: drustz-1e8a11b02f29f1cfa9
section: forum-notes
order: 35
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 4: Merging and History'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 4: Merging and History'
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
## Level 4: Merging and History

### Goal

Combine two accounts into one. The new account keeps the money and history of both. You also need to look up balances from the past.

### New Functions

#### merge_accounts

```text
merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool
```



- **Action:** Merge Account 2 *into* Account 1.
- **Result:**

Account 1 gets all of Account 2's money.
- Account 1 inherits Account 2's spending history (for `top_spenders`).
- Any cashback Account 2 was waiting for will now go to Account 1.
- You can look up Account 2's old payment statuses using Account 1's ID.
- Account 2 is **deleted** from the system.
- **Returns `True`:** If the merge works.
- **Returns `False` if:**

You try to merge an account into itself.
- Either account does not exist.

#### get_balance

```text
get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None
```



- **Action:** Find out how much money `account_id` had at a specific time (`time_at`).
- **Returns:** The balance at that exact moment.
- **Returns `None`:** If the account did not exist at that time.
- **Note:** If an account was merged, the main account inherits the history.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
