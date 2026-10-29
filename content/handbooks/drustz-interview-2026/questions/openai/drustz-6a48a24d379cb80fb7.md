---
id: drustz-6a48a24d379cb80fb7
section: openai
order: 177
level: A
title: 'Resumable Iterator, Unit Tests, Time-Based KV Store, and Concurrency'
quick: >-
  original-structured-preparation-guide · Resumable Iterator, Unit Tests,
  Time-Based KV Store, and Concurrency
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
      https://www.1point3acres.com/interview/problems/ec3912e2-0511-4700-b01b-5fad7ac3d781
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Resumable Iterator + Time-Based KV + Concurrency

> 标题包含多个独立部分。旧正文只有 iterator 主体；这里补齐 KV 与并发要求。

## Iterator

state 只保存可序列化游标，不保存文件句柄或锁。List/多维 iterator 保存 index stack；`get_state/set_state` 必须 round-trip，`has_next` 不能推进。

## Time-Based KV

```text
set(key, value, timestamp)
get(key, timestamp) -> 不晚于查询时间的最新值
```



同 key timestamp 单调时列表 append `O(1)`，查询 `bisect_right` 为 `O(log m)`；允许乱序则数组插入 `O(m)` 或改用平衡树。

时间通过参数或 injectable Clock 提供，测试使用 fake clock，不能真实 sleep。

## Concurrency

全局锁简单但完全串行；per-key/striped lock 让不同 key 并行；读多写少可讨论 RWLock。跨 key 操作按固定锁顺序，防止死锁。serialization 保存 schema version、游标和标量，恢复时校验版本。

## 边界

同 timestamp 覆盖规则、早于首条记录、乱序写、并发 read/write、恢复旧 schema、游标越界、空 iterator 和异步 iterator 的 pending work。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/ec3912e2-0511-4700-b01b-5fad7ac3d781)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
