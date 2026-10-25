---
id: ali-algo-lru
section: alibaba-oa
order: 34
level: S
title: 阿里手撕：LRU 为什么是哈希 + 双向链表？
quick: >-
  哈希表 $O(1)$ 找到节点，双向链表 $O(1)$ 把节点搬到表头、从表尾淘汰。只用哈希没有访问顺序，只用链表查找是 $O(n)$；节点里还要存 key，淘汰时才能顺手删掉哈希里的映射。
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

## 题目描述

实现固定容量的最近最少使用缓存 `LRUCache`。缓存保存整数 key 到整数 value 的映射；每次成功读取或写入，都使该 key 成为最近使用的条目。

### 接口与约定

- `LRUCache(capacity)`：建立空缓存，`capacity` 是正整数，缓存中的条目数不能超过它。
- `get(key)`：key 存在时返回对应 value，并更新它的使用顺序；不存在时返回 `-1`，不影响其他条目的顺序。
- `put(key, value)`：已有 key 时更新 value 和使用顺序；新 key 时插入。若因此超出容量，移除最后一次被成功读取或写入的时间最早的条目。此方法不返回业务值。

要求 `get` 和 `put` 的平均时间复杂度均为 O(1)。输入均符合接口约定，不要求实现多线程、过期时间或分布式功能。

### 示例

```text
c = LRUCache(2)
c.put(1, 1); c.put(2, 2)
c.get(1) -> 1
c.put(3, 3)
c.get(2) -> -1
c.put(4, 4)
c.get(1) -> -1
c.get(3) -> 3
c.get(4) -> 4
```

这里采用手册的独立 Python 类接口。

## 解题思路与参考答案

LRU 要求 `get` 和 `put` 都是 $O(1)$，一个结构做不到，所以用哈希表负责定位、双向链表负责顺序。只有哈希就没有访问顺序，只有链表查找是 $O(n)$。这是 LeetCode 146，阿里 Java 面几乎必问。

先把行为说清楚。`get` 命中就把节点移到最近使用的一端并返回值，没命中返回 $-1$。`put` 遇到已有的 key 就更新值、移到最近端；新 key 就插进去，超出容量时删掉最久没用的那个。比如容量是 2，先放 1、2，`get(1)` 之后 1 变成最近用过的，这时再放 3，被挤掉的就是 2。

写法上我会加哑头和哑尾两个节点，空表和单节点就和普通情况走同一套指针操作。约定头侧是最近使用、尾侧是最久未用。`_remove(node)` 让左右邻居互指，跳过自己；`_append_front(node)` 插到哑头后面。`get` 命中时先 `_remove` 再 `_append_front`。`put` 已有 key 就改值、搬到头；新 key 先插到头，超容量就删掉哑尾前面那个节点，并 `del map[key]`。节点里存 key 就是为了这一步：从链表摘下来以后，得知道去哈希里删哪个。

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

`get` / `put` 均摊 $O(1)$，空间 $O(\mathrm{capacity})$。用 `OrderedDict` 写也行，但要讲清楚它底下怎么搬节点，否则等于没答。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert c.get(1) == 1` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**`capacity=1`、重复 `put` 同一个 key 这类边界怎么处理？**
已有 key 先更新，再判断要不要淘汰，避免刚写进去的值被自己挤掉。`get` 没命中就返回 $-1$。

**要加 TTL 呢？**
节点里加过期时间，`get` 时惰性删除；容量满了可以先清掉过期的，再按 LRU 淘汰。

**多线程或者分布式怎么办？**
单机加一把锁，或者用分段锁。跨进程就交给 Redis 的 `maxmemory-policy`，比如 `allkeys-lru`，面试里别去手写分布式链表。
