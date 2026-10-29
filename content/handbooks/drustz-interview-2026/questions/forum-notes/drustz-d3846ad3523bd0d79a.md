---
id: drustz-d3846ad3523bd0d79a
section: forum-notes
order: 34
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 3: Payments and Cashback'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 3: Payments and Cashback'
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

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
