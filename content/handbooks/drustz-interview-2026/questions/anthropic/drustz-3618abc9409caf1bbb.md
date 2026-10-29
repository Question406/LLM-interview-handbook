---
id: drustz-3618abc9409caf1bbb
section: anthropic
order: 30
level: A
title: OA Bank System
quick: locally-saved-topic-editorial · OA Bank System
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/oa-bank-system
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Banking System (Online Assessment)

### System Overview

You need to build a bank system that runs in the computer's memory. There are **4 levels** to this problem. You must finish one level to move to the next.

- **Level 1:** create accounts, add money, and move money between accounts.
- **Level 2:** Rank accounts by how much they spend.
- **Level 3:** Schedule payments and handle cashback rewards.
- **Level 4:** Merge two accounts and look up old balances.
You will keep all data from previous levels as you move forward.

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

## Level 3: Payments and Cashback

### Goal

Add a feature to pay for things. Every payment gets **2% cashback** refund after 24 hours. You also need to check the status of these payments.

### New Functions

#### pay

```text
pay(self, timestamp: int, account_id: str, amount: int) -> str | None
```



- **Action:** Subtract `amount` from the account.
- **Cashback Rule:** The user earns 2% of the transaction amount. Round this down to the nearest whole number.
- **Timing:** The cashback is added back to the account exactly **24 hours** later.

24 hours = 86,400,000 milliseconds.
- Refund time = `timestamp + 86400000`.
- **Returns:** A unique ID string for this payment (e.g., `"payment1"`).
- **Returns `None` if:**

The account does not exist.
- The account does not have enough money.
- **Note:** This withdrawal counts towards the "outgoing money" used in `top_spenders`.

#### get_payment_status

```text
get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None
```



- **Action:** Check the status of a specific payment.
- **Returns:**

`"IN_PROGRESS"`: If the cashback has not arrived yet.
- `"CASHBACK_RECEIVED"`: If the cashback has been added to the account.
- **Returns `None` if:**

The account or payment ID does not exist.
- The payment ID belongs to a different account.

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

## Special Rules & Edge Cases

### Recreating an Account

- If Account B is merged into Account A, Account B is deleted.
- You are allowed to create a **new** Account B later.
- This new Account B starts with &#36;0. It does not have the history of the old Account B (because that history moved to Account A).

### History Checks

- Imagine Account B merged into Account A at time `T`.
- If you ask for Account B's balance **before** time `T`: You get the old balance.
- If you ask for Account B's balance **after** time `T`: You get `None` (unless you created a new Account B).

## System Constraints

- **Timestamps:** Numbers representing milliseconds. They are always unique and always increase.
- **IDs:** Valid text strings.
- **Amounts:** Positive whole numbers.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100004*)

---

---

### 用户本地练习实现（已通过对应单元测试）

- practice/anthropic/banking_system_full.py
- 测试：tests/test_banking_system_full.py

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/oa-bank-system)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
