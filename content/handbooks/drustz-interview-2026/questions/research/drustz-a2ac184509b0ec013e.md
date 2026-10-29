---
id: drustz-a2ac184509b0ec013e
section: research
order: 33
level: A
title: >-
  Design Banking System (4-level OA/onsite; the classic CodeSignal banking
  series)
quick: >-
  supplemental-research-note · Design Banking System (4-level OA/onsite; the
  classic CodeSignal banking series)
companies:
  - anthropic
tags:
  - DrustZ
  - supplemental-research-note
  - 公司面试 · 补充研究笔记
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/687c23f9aa2b26b0b64b39d4
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开预览与可核实要点。

Stages: OA + Onsite. BankingSystem class, all ops timestamped with increasing ints. Level 1 (q 687c3a5e...): createAccount(ts,accountId)->bool (false if exists); deposit(ts,accountId,amount)->new balance or -1; transfer with validations (existence, distinct IDs, sufficient funds) all checked before committing. Level 2 (q 687c4741...): topSpenders(n) - rank accounts by cumulative OUTGOING transaction totals desc, tie-break alphabetical ID asc, format top N; maintain running outgoing sums instead of recomputing. Level 3 (q 687c4e56...): pay(ts,accountId,amount) deducts and schedules 2% cashback credited exactly 24h (86400000ms) later; getPaymentStatus(ts,accountId,payment)-> IN_PROGRESS/CASHBACK_RECEIVED; cashbacks due at a timestamp must be applied BEFORE any other operation at that timestamp; rounding down on 2%. Level 4 (q 687c5c0b...): mergeAccounts(id1,id2) consolidating balances, transaction history and pending cashbacks; getBalance(ts,accountId,timeAt) historical balance queries incl. accounts merged away before query time; self-merge invalid. Site follow-ups: thread safety; audit logging; float precision for currency; scaling to millions of tx; atomicity; prefix-sum/indexed history for O(log n) historical queries.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/687c23f9aa2b26b0b64b39d4)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
