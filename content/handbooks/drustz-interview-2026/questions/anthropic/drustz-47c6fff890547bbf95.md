---
id: drustz-47c6fff890547bbf95
section: anthropic
order: 5
level: A
title: Coding Q2 LRU Cache Durability
quick: locally-saved-topic-editorial · Coding Q2 LRU Cache Durability
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
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-q2-lru-cache-durability
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## LRU Cache (Python)

## The Problem

You are given a Python code for an in-memory LRU (Least Recently Used) cache. The code works, but there is a mistake in how it creates keys.

The error happens when the cache tries to handle variable arguments (`*args`) and keyword arguments (`**kwargs`).

Your task is to:

- **Read** the current code and see how it works.
- **Find the mistake** in the key creation step.
- **Fix the code** so it handles `*args` and `**kwargs` correctly.

### What You Need to Do

Your solution must:

- **Find the error** — Understand why `*args` and `**kwargs` break the current key maker.
- **Make keys hashable** — Change arguments into a format that can be used as dictionary keys.
- **Handle all arguments** — Work correctly with both `*args` and `**kwargs`.
- **Keep the cache accurate** — Ensure the same inputs always create the exact same key.

### Helpful Tips

- **Python Knowledge**: You need to know:

How `*args` and `**kwargs` work in Python.
- Which data types work as dictionary keys (hashable) and which do not.
- How to change arguments into a hashable format.
- **Hints**:

Remember that keyword arguments can be in any order. For example, `func(a=1, b=2)` is the same as `func(b=2, a=1)`.
- Think about changing unhashable types (like lists or dicts) into hashable types (like tuples or frozensets).
- Check Python's `functools` library for ideas.

## Part 2: Saving Data to Disk

After fixing the bug, you need to update the cache to save data to the disk. The system must:

- **Recover after a crash** — If the program stops or restarts, it should reload the old data.
- **Save data safely** — Do not lose data during normal use or if the program crashes.
- **Keep LRU order** — The saved data must remember which items were used most recently.

### System Requirements

- **Save to disk** — Store cache items in a file.
- **Reload on start** — Read the file and fill the cache when the program begins.
- **Keep data matching** — Make sure the memory cache and the file have the same data.
- **Watch speed** — Find a balance between writing fast and saving safely.

### Things to Discuss

**Discussion Points:**

- **File Format**:

How will you save the data (JSON, pickle, or a custom format)?
- Should you use one file or many files?
- **How to Write**:

Write-through: Save to disk every time (slow but safe).
- Write-back: Save in groups later (fast but risky).
- Append-only log: Add new changes to the end of a log file.
- **How to Recover**:

How do you rebuild the LRU order?
- Do you need extra data like timestamps?
- **Speed vs. Safety**:

Blocking writes vs. non-blocking (async) writes.
- Choosing between speed and data safety.
- The cost of Disk I/O.

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

### 用户本地练习实现（已通过对应单元测试）

- practice/anthropic/durable_function_call_cache.py
- 测试：tests/test_durable_function_call_cache.py

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q2-lru-cache-durability)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
