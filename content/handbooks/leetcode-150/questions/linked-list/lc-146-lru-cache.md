---
id: lc-146-lru-cache
section: linked-list
order: 11
level: S
title: LC 146 · LRU 缓存
quick: >-
  哈希定位节点，双向链表维护新旧：头是最近使用，尾是最久未用。`get` / `put` 都把节点移到头，满则淘汰尾巴。均摊
  $O(1)$。
tags:
  - Hash
  - Design
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 146. LRU 缓存
    url: https://leetcode.cn/problems/lru-cache/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

实现 `LRUCache`：`get(key)` 存在则返回值并视为刚使用，否则 $-1$；`put(key, value)` 更新或插入，容量满时淘汰最久未使用的键。`get` / `put` 均摊 $O(1)$。

## 思路

哈希表 `key ->` 链表节点，随机访问 $O(1)$。双向链表按使用时间排：哑头之后是最近使用，哑尾之前是最久未用。命中就摘下再插到头；插入新键也放头；超容量删尾巴并同步删哈希。

必须双向：单向无法 $O(1)$ 删中间节点。哑头尾省掉空表特判。面试先讲清两套结构各管什么，再写 `_remove` / `_add_to_head`。

## 参考代码

```python
from typing import Dict, Optional


class ListNode:
    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev: Optional["ListNode"] = None
        self.next: Optional["ListNode"] = None


class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map: Dict[int, ListNode] = {}
        self.head = ListNode()
        self.tail = ListNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: ListNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_head(self, node: ListNode) -> None:
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._add_to_head(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            node = self.map[key]
            node.val = value
            self._remove(node)
            self._add_to_head(node)
            return
        if len(self.map) == self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]
        node = ListNode(key, value)
        self.map[key] = node
        self._add_to_head(node)


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
    d = LRUCache(1)
    d.put(2, 1)
    assert d.get(2) == 1
    d.put(3, 2)
    assert d.get(2) == -1 and d.get(3) == 2
    print("ok")
```

## 复杂度

`get` / `put` 时间 $O(1)$。空间 $O(\textit{capacity})$，哈希与链表各存一份节点引用。

## 边界

- 容量为 $1$：每次 `put` 新键都会淘汰唯一节点。
- `put` 更新已有键也算一次使用，必须移到头。
- 连续 `get` 未命中不改链表顺序。
- 先 `put` 满再 `get` 再 `put`：淘汰的是当前尾巴，不是插入顺序里最早的。

## 追问

- **改成 LFU（LC 460）？** 除了键到节点的哈希，再按频次分层：每个频次一条双向链表（同频内仍是 LRU，尾巴最久）。节点额外记 `freq`。`get`/`put` 命中时把节点从旧频次链表摘下，`freq+1` 后插入新层头部；若旧层空且它是 `min_freq`，则 `min_freq` 加一。插入新键时频次为 $1$，`min_freq=1`；满则淘汰 `min_freq` 层的尾巴，并同步删哈希。必须双向链表才能 $O(1)$ 删中间节点。均摊 $O(1)$。容量为 $0$ 直接忽略 `put`。

```python
class LFUCache:
    def __init__(self, capacity):
        self.cap, self.minf = capacity, 0
        self.key_map, self.freq_map = {}, {}

    def _new_list(self):
        h, t = ListNode(), ListNode()
        h.next, t.prev = t, h
        return h, t, 0

    def _remove(self, node):
        node.prev.next, node.next.prev = node.next, node.prev
        h, t, sz = self.freq_map[node.freq]
        self.freq_map[node.freq] = (h, t, sz - 1)

    def _add_front(self, node):
        if node.freq not in self.freq_map:
            self.freq_map[node.freq] = self._new_list()
        h, t, sz = self.freq_map[node.freq]
        node.next, node.prev = h.next, h
        h.next.prev = h.next = node
        self.freq_map[node.freq] = (h, t, sz + 1)

    def _bump(self, node):
        self._remove(node)
        _, _, sz = self.freq_map[node.freq]
        if sz == 0 and self.minf == node.freq:
            self.minf += 1
        node.freq += 1
        self._add_front(node)

    def get(self, key):
        if key not in self.key_map:
            return -1
        node = self.key_map[key]
        self._bump(node)
        return node.val

    def put(self, key, value):
        if self.cap == 0:
            return
        if key in self.key_map:
            node = self.key_map[key]
            node.val = value
            self._bump(node)
            return
        if len(self.key_map) == self.cap:
            h, t, sz = self.freq_map[self.minf]
            lru = t.prev
            self._remove(lru)
            del self.key_map[lru.key]
        node = ListNode(key, value)
        node.freq = 1
        self.key_map[key] = node
        self._add_front(node)
        self.minf = 1
```

- **线程安全 / 分布式？** 单机加一把锁（或读写锁）包住「查哈希 + 搬节点」，否则两个线程同时 `get` 会把链表指针拧乱。不要只锁哈希不锁链表。分布式不能靠一台机器上的双链表：用一致性哈希把键分到分片，每片各自 LRU，再加 TTL / 版本号处理过期与并发写。跨分片没有全局「最久未用」，只能近似。面试把单机 $O(1)$ 与分布式分片分开讲。
