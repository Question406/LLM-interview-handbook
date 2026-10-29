---
id: drustz-0e45bc7f43e60cfaa4
section: openai
order: 178
level: A
title: AccountBalance Class with Time-Based Grants and Spending
quick: >-
  original-structured-preparation-guide · AccountBalance Class with Time-Based
  Grants and Spending
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/fb4a851c-1fca-4576-9ec6-c933f106c6d4
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# AccountBalance：有起止时间的 Grant 与 Spend

## 证据边界与练习合同

公开题面要求 `addGrant(amount,timestamp,expire)`、`addSpend(amount,timestamp)`、`getBalance(timestamp)`，余额排除已过期 grant，交易按时间顺序处理；但未说明调用是否乱序、过期端点、同刻顺序、从哪个 grant 扣款或余额不足返回值。为得到可测实现，本指南选择：grant 在 `[timestamp,expire)` 有效；方法可乱序到达，但查询按 `(timestamp,type_order,arrival_seq)` 重放，同刻先 grant 后 spend；spend 优先消耗最早过期额度；余额不足则整笔返回 `False` 且不部分扣。面试时必须把这些选择复述确认，不能称为会员原文。

例：`addGrant(100,1,5)`、`addGrant(50,2,10)`、`addSpend(120,3)`；按最早过期先用完第一笔，再用第二笔 20，所以 `getBalance(4)=30`，`getBalance(6)=30`。时刻 7 再 spend 40 因不足而失败，余额仍 30。若采用本地另一变体“不足后查询返回 None”，状态机与返回合同都不同，应单独实现。

## 重放解法、复杂度与乱序语义

保存不可变 event ledger。计算时筛出 `timestamp<=t` 的事件并排序，使用按 expire 的最小堆保存 `[expire,remaining,id]` 和 running total；每个事件前弹出 `expire<=event_time` 的 grant。spend 先检查 active total，足够才从堆顶逐笔扣；getBalance 在处理完目标时刻事件后返回 total。这样后来到达但 timestamp 更早的事件会改变后续查询结果，缓存必须从最早受影响点失效；若接口保证调用时间单调，则可在线维护堆，把每次操作降为摊销 `O(log G)`。

从头重放 `E` 个事件需排序 `O(E log E)`、处理 `O(E log G)`、空间 `O(E+G)`。边界测试 `timestamp==expire`、expire≤start、浮点 amount 精度、同刻 grant/spend/query、乱序插入后重复查询、跨多个 grant 扣款、余额刚好用完、失败不部分写、过期未用余额、负金额，以及相同 expire 的确定 tie-break。实际金额宜用整数最小单位或 Decimal，避免 float 误差。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/fb4a851c-1fca-4576-9ec6-c933f106c6d4)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
