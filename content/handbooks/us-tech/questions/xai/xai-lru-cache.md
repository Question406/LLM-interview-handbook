---
id: xai-lru-cache
section: xai
order: 9
level: A
title: xAI：手写 LRU / 并发缓存，和 KV 事务题怎么衔接
quick: >-
  Hash map 加双向链表，$O(1)$ get/put。并发按 key 分片，不要一把大锁。接到 KV 事务：缓存的是已提交快照，未提交写不能被逐出成别人的可见值。
tags:
  - xAI
  - LRU
  - Concurrency
  - Cache
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Get a Job at xAI — Interview Process and Top Questions
    url: https://www.tryexponent.com/blog/xai-interview-process
    type: secondary
  - title: xAI Software Engineer Interview Guide
    url: https://www.tryexponent.com/guides/xai-software-engineer-interview
    type: secondary
  - title: xAI Interview Questions from Candidate Reports
    url: https://aceoffer.app/interviews/xai
    type: secondary
  - title: Practice xAI Mock Interviews
    url: https://igotanoffer.com/en/mock-interviews/company/xai
    type: secondary
---

## 题怎么来的

Exponent / AceOffer 把 LRU（含加权变体）列为 xAI coding 高频，和 KV 事务、rate limiter 同一筐：能跑的类、边界、并发，不是链表 trivia。`realInterview: false`，按公开题库准备。衔接点是 `xai-kv-txn`：事务要快照隔离，缓存是快照的物化，逐出策略不能破坏隔离。

## 先写对 $O(1)$，再加容量

结构：`dict[key] -> node`，node 串在双向链表上。链表头是最新，尾是最旧。`get` 命中则挪到头；`put` 已存在则更新并挪头，满了删尾。

```python
class Node:
    def __init__(self, key, val):
        self.key, self.val = key, val
        self.prev = self.nxt = None


class LRUCache:
    def __init__(self, cap):
        self.cap = cap
        self.map = {}
        self.head = Node(None, None)  # dummy
        self.tail = Node(None, None)
        self.head.nxt = self.tail
        self.tail.prev = self.head

    def get(self, k):
        node = self.map.get(k)
        if not node:
            return None
        self._pull(node)
        self._to_head(node)
        return node.val

    def put(self, k, v):
        if k in self.map:
            node = self.map[k]
            node.val = v
            self._pull(node)
            self._to_head(node)
            return
        node = Node(k, v)
        self.map[k] = node
        self._to_head(node)
        if len(self.map) > self.cap:
            old = self.tail.prev
            self._pull(old)
            del self.map[old.key]
```

`_pull` / `_to_head` 只改四根指针。错法：用 `list` 当队列再 `index`，那是 $O(n)$；满了删头而不是尾；`get` 不更新顺序。加权 LRU（AceOffer 提过）：节点带 `weight`，容量是重量和，逐出时仍从最旧开始，直到腾出足够重量。单测：cap=2 时 `put a,b,c` 后 `get a` 应 miss。

## 并发：分片，不要和事务抢同一把锁

一把全局锁能写对，吞吐难看。按 `hash(key) % N` 分片，每片自己的 map+链表+锁。跨片没有事务的话这就够。`get` 只锁一片。

和 `xai-kv-txn` 衔接是这轮加分：

1. **缓存里只放已提交版本。** 事务写缓冲在 commit 成功前不要 `put` 进共享 LRU，否则别的读会看到脏数据，快照隔离碎了。
2. **commit 后按版本号 put。** 迟到的旧 commit 不能覆盖新版本：`if incoming.ver < cached.ver: ignore`。
3. **逐出不等于 abort。** LRU 丢掉的是副本，源 KV 还在。但若你把 LRU 当主存（面试常这样简化），逐出就是删 key，要和事务的写集核对：未提交 key 被逐出，commit 时还得能写回去，或者禁止逐出「有活跃写锁」的节点。
4. **读快照。** 事务 begin 时记下版本，`get` 走缓存若 `cached.ver > begin.ver` 要回源到旧版本，或直接 miss 回主结构。缓存命中不是「最新就好」。

TTL 当 follow-up：过期和 LRU 是两条轴，惰性删（get 时看 `expire_at`）加容量逐出。不要和 `xai-rate-limiter` 的时间窗搅成一个桶——限流是配额，缓存是副本。

错法：用 `dict` 的插入顺序当 LRU 却在面试语言里说不清；并发下 `get` 挪链表不持锁；把缓存当事务日志。

## 追问

- **为什么不用单链表？** 删尾和挪节点需要 $O(1)$ 的前驱，双向更干净。
- **分片会不会让全局容量不准？** 每片 `cap/N`，最坏一块热、一块空。可接受；要更准再用全局计数加近似 LRU（CLOCK）。先正确再近似。
- **和 KV 事务哪句最重要？** 未提交写不可见。LRU 是已提交状态的加速层，不是写缓冲。
- **加权变体怎么测？** 放大对象应挤掉多个小对象；`get` 仍只更新时间，不改重量，除非题目要求 size 随值变。
