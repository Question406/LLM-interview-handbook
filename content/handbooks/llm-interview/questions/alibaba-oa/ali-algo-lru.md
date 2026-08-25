---
id: ali-algo-lru
section: alibaba-oa
order: 34
level: S
title: 阿里手撕：LRU 为什么是哈希 + 双向链表？
quick: >-
  哈希 $O(1)$ 找节点，双向链表 $O(1)$ 搬到表头、删表尾。只哈希没有顺序，只链表查找是 $O(n)$。
tags:
  - Alibaba
  - LRU
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: LRU 缓存
    url: https://leetcode.cn/problems/lru-cache/
    type: primary
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6
    type: candidate-first-hand
---

## 真题 / 考点说明

- 对应：LeetCode 146；阿里 Java 面几乎必问

`get`：命中就把节点移到最近端，返回值；未命中返回 $-1$。`put`：存在则更新并移到最近端；不存在则插入，超容量删最久未用。

哈希负责 $O(1)$ 定位，双向链表负责 $O(1)$ 调整顺序。只哈希没有访问顺序，只链表查找是 $O(n)$。节点里要存 key，淘汰时才能删哈希。

## 思路

哑首尾节点把空表和单节点变成同一套指针操作。约定：头侧是最近使用，尾侧是最久未用。

- `_remove(node)`：左右互指，跳过自己。
- `_append_front(node)`：插到哑头后面。
- `get`：命中则 `_remove` + `_append_front`。
- `put`：已有则改值并搬到头；新 key 先插头，超容量则删哑尾前面那个，并 `del map[key]`。

线程安全：单机一把锁或分段锁；分布式不是手写链表，而是 Redis `maxmemory-policy`。

## 参考代码

```python
from __future__ import annotations

from typing import Dict, Optional


class _Node:
    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev: Optional["_Node"] = None
        self.next: Optional["_Node"] = None


class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map: Dict[int, _Node] = {}
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _append_front(self, node: _Node) -> None:
        nxt = self.head.next
        node.prev = self.head
        node.next = nxt
        self.head.next = node
        nxt.prev = node

    def get(self, key: int) -> int:
        node = self.map.get(key)
        if node is None:
            return -1
        self._remove(node)
        self._append_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        node = self.map.get(key)
        if node is not None:
            node.val = value
            self._remove(node)
            self._append_front(node)
            return
        node = _Node(key, value)
        self.map[key] = node
        self._append_front(node)
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]


if __name__ == "__main__":
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1
    c.put(3, 3)
    assert c.get(2) == -1
    c.put(4, 4)
    assert c.get(1) == -1
    assert c.get(3) == 3
    assert c.get(4) == 4
    print("ok")
```

## 复杂度

`get` / `put` 均摊 $O(1)$，空间 $O(\mathrm{capacity})$。不要用 `OrderedDict` 充数却讲不清搬节点。

## 边界与追问

1. `capacity=1`、重复 `put` 同一 key、`get` 未命中：容量满时先更新再判淘汰，避免刚写入就被自己挤掉。
2. 追问 TTL：节点加过期时间，`get` 惰性删；容量满可先清过期再 LRU。
3. 追问并发 / 分布式：单机锁或分段；跨进程用 Redis `allkeys-lru`，不要在面试里手写分布式链表。
