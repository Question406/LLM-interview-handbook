---
id: drustz-d08edacd5535b919d0
section: openai
order: 90
level: A
title: Design an in-memory rate limiter (token bucket / sliding window)
quick: >-
  original-structured-preparation-guide · Design an in-memory rate limiter
  (token bucket / sliding window)
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
      https://www.1point3acres.com/interview/problems/91b46503-5a56-4b8a-a1f3-b4f15da02b11
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 设计内存中的线程安全限流器

## 题目要做什么

实现：

```text
allow(key: str, now_ms: int) -> bool
```



每个 key 独立限流。策略可以是：

- 滑动窗口：任意 `window_ms` 内最多允许 `limit` 次；
- Token bucket：桶容量为 `limit`，按照 `limit / window_ms` 的速率补充 token。

规模可能达到约 `10^6` 次调用和 `10^5` 个 key，还要考虑线程安全与长期闲置 key 的清理。

## Token bucket 解法

每个 key 保存：

```text
tokens, last_refill_time
```



在同一个 key 锁或 shard 锁内：

1. `elapsed = max(0, now - last_refill_time)`；
2. 补充 `elapsed * rate` 个 token，但不超过容量；
3. 如果至少有 1 个 token，就扣除并返回 `True`；
4. 否则返回 `False`。

Token bucket 允许一定突发流量。若题目要求严格的任意滑动窗口，应改成每个 key 一个 deque：删除 `timestamp <= now - window` 的旧记录，再检查长度。

## 并发与清理

不要为所有 key 使用一把全局锁。可按 key 哈希到固定数量的 shard 锁，在锁内同时完成补充、判断和扣减。清理闲置 key 时也必须使用同一 shard 锁，避免清理线程删除一个正在使用的 bucket。

## 复杂度

- Token bucket：每次 `O(1)`，空间为 `O(活跃 key 数)`；
- Sliding-window log：每次摊销 `O(1)`，最坏空间为 `O(key 数 × limit)`。

## 边界

乱序时间、相同时间的大量请求、`limit = 0`、浮点精度、闲置 key 回收竞争、窗口端点与 shard 热点。如果允许任意历史时间查询，普通在线 limiter 不再正确，必须重新定义语义。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/91b46503-5a56-4b8a-a1f3-b4f15da02b11)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
