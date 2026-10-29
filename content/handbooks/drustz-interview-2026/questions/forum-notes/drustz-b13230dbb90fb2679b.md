---
id: drustz-b13230dbb90fb2679b
section: forum-notes
order: 32
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 1: Basic Actions'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 1: Basic Actions'
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
## Level 1: Basic Actions

### Goal

Start with an empty bank. Write code to create accounts, put money in, and send money to others.

### Functions to Write

#### create_account

```text
create_account(self, timestamp: int, account_id: str) -> bool
```



- **Action:** Create a new account with the name `account_id`.
- **Returns `True`:** If the account is new and created successfully.
- **Returns `False`:** If that name is already taken.

#### deposit

```text
deposit(self, timestamp: int, account_id: str, amount: int) -> int | None
```



- **Action:** Add `amount` to the account.
- **Returns:** The new total balance after the deposit.
- **Returns `None`:** If the account does not exist.

#### transfer

```text
transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None
```



- **Action:** Move `amount` from the source account to the target account.
- **Returns:** The new balance of the source account if successful.
- **Returns `None` if:**

Either account does not exist.
- You try to transfer money to yourself (source and target are the same).
- The source account does not have enough money.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
