---
id: drustz-613ff5f61d3c77f84f
section: forum-notes
order: 104
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Extra Questions
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Extra Questions
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
## Extra Questions

These questions are for talking only. You do not need to write code. Be ready to explain your thoughts.

### 1. Ways to Remove Old Data

**Question:** Besides LRU, what other rules can we use to remove items from the cache? When is each one useful?

**Discussion Points:**

- **LRU (Least Recently Used)**: Remove the item not used for the longest time.
- **LFU (Least Frequently Used)**: Remove the item used the least amount of times.
- **FIFO (First In First Out)**: Remove the oldest item added.
- **Random**: Remove an item by chance.
- **TTL (Time To Live)**: Remove items after a set time expires.
- **Trade-offs**: Each rule is good for different situations.

### 2. Caching Across Multiple Computers

**Question:** How would you make this cache work on many computers in a distributed system?

**Discussion Points:**

- **Consistency**: How to keep data the same everywhere.

Shared distributed cache (like Redis or Memcached).
- Strategies to delete old data (invalidation).
- Eventual consistency vs strong consistency.
- **Partitioning**: How to split data between computers.

Consistent hashing.
- Splitting by range.
- **Replication**: Copying data so it is safe if one computer fails.
- **Network**: The cost of sending data between computers.

### 3. Handling Multiple Users (Concurrency)

**Question:** How would you make the cache safe if many threads use it at the same time?

**Discussion Points:**

- **Locking**:

Global lock (easy but slow).
- Fine-grained locking (faster but harder to code).
- Read-write locks (good for many reads).
- **Lock-free**: Using atomic operations.
- **Tools**: Mutexes, semaphores, condition variables.
- **Deadlocks**: How to avoid getting stuck.
- **Speed**: How locks affect performance.

### 4. Managing Memory Usage

**Question:** How do you stop the cache from using too much RAM?

**Discussion Points:**

- **Limits**:

Max number of items.
- Max memory usage.
- Size limit per item.
- **Measuring**: How to calculate the size of an object.
- **When to clear**: When to start removing items.
- **Pressure**: Cleaning up before the system runs out of memory (OOM).
- **Trade-offs**: Balancing cache hits vs. using memory.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100002*)

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
