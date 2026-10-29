---
id: drustz-31ac3bdbdfb67000a9
section: openai
order: 124
level: A
title: 'Coding: Credit/Bug-free Implementation'
quick: 'original-structured-preparation-guide · Coding: Credit/Bug-free Implementation'
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
      https://www.1point3acres.com/interview/problems/68125203-6fe0-48a1-ad34-b40da1720c20
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Credit / Bug-free Implementation：来源映射有冲突

> OJ 描述只说实现 credit 相关 API，但其关联帖的公开摘要偏向 iOS onsite。两者证据不一致，不能把下面练习标成这条 UUID 的原题。

## 同题家族原创练习

设计一个额度账本：

```text
add_grant(id, amount, start, end)
spend(time, amount)
balance(time)
```



每笔 grant 在半开区间 `[start, end)` 内有效；消费时优先使用最早过期的额度；事件可能乱序到达。

## 基础正确解法

把 grant 和 spend 保存成 event log。查询某个时间点时，按 `(timestamp, 同时刻事件顺序)` 重放：

1. 加入已经开始生效的 grant；
2. 移除已经过期的 grant；
3. spend 使用按过期时间排序的最小堆，优先扣最早到期额度；
4. 余额不足时整个 spend 必须原子失败；
5. 插入历史事件后，让该时间之后的 checkpoint 失效。

同一个 timestamp 下 grant、spend 和 query 的先后顺序必须在 API 合同中明确。

## 复杂度

基础重放版排序为 `O(E log E)`，重放为 `O(E log G)`，空间为 `O(E + G)`。可用 checkpoint 加速重复查询，但乱序插入会使后续缓存失效。

## 边界

重复 grant ID、余额不足、半开区间端点、同时间事件、部分消费、乱序插入、浮点金额和重试造成重复扣款。金额应使用整数最小货币单位或 Decimal，而不是二进制浮点数。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/68125203-6fe0-48a1-ad34-b40da1720c20)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
