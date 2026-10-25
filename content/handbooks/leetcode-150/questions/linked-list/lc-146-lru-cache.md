---
id: lc-146-lru-cache
section: linked-list
order: 11
level: S
title: LC 146 · LRU 缓存
quick: "哈希表负责定位节点，双向链表按使用时间排序，头是最近使用、尾是最久未用。`get` 和 `put` 都把节点移到头，满了就淘汰尾巴，均摊 $O(1)$。"
tags:
  - Hash
  - Design
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 146. LRU 缓存
    url: https://leetcode.cn/problems/lru-cache/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

实现固定容量的最近最少使用缓存。缓存保存整数键和值；容量不足以容纳一个新键时，删除距离上一次被访问最久的键。读取命中的键、插入新键和更新已有键都会使该键成为最近使用的键。

### 输入与输出

实现 `LRUCache(capacity)`、`get(key) -> int` 和 `put(key, value) -> None`。构造时为空。get 命中返回值，未命中返回 -1，未命中不会创建键；put 更新已有键时不增加键数，插入新键导致超容量时执行一次淘汰。两种操作都要求平均 `O(1)` 时间。

### 约束与约定

- `1 <= capacity <= 3000`。
- 键在 `[0,10000]`，值在 `[0,100000]`。
- get 与 put 总调用次数不超过 200000。

### 示例

```text
输入：["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
输出：[null, null, null, 1, null, -1, null, -1, 3, 4]
```

示例第一行是构造器及方法名，第二行是对应参数。输出的 null 对应构造器和没有返回值的 put；get 输出实际查询结果。

[官方原题与完整题面](https://leetcode.com/problems/lru-cache/description/)。

## 解题思路与参考答案

## 题意

实现 `LRUCache`。`get(key)` 存在就返回值并算作刚用过，否则返回 $-1$；`put(key, value)` 更新或插入，容量满时淘汰最久没用的键。`get` / `put` 都要均摊 $O(1)$。

## 思路

我用哈希表加双向链表，哈希负责 $O(1)$ 找到节点，链表负责 $O(1)$ 调整新旧顺序。哈希表存 `key ->` 链表节点；链表里哑头之后是最近使用的，哑尾之前是最久未用的。命中就把节点摘下来插到头，插入新键也放到头，超容量就删掉尾巴，同时删掉哈希里的键。

拿测试里容量为 $2$ 的例子走一遍。`put(1)`、`put(2)` 之后链表是 2、1；`get(1)` 把 1 挪到头，变成 1、2；这时 `put(3)`，容量满了，淘汰的是尾巴上的 2，所以接下来 `get(2)` 返回 $-1$。

链表必须是双向的，单向链表没法 $O(1)$ 删掉中间的节点。哑头和哑尾省掉了空表的特判。开口我会先讲清两套结构各管什么，再写 `_remove` 和 `_add_to_head`。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
c = LRUCache(2)
c.put(1, 1)
c.put(2, 2)
assert c.get(1) == 1
c.put(3, 3)
assert c.get(2) == -1
c.put(4, 4)
assert c.get(1) == -1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

`get` / `put` 时间 $O(1)$。空间 $O(\textit{capacity})$，哈希与链表各存一份节点引用。

## 边界

- 容量为 $1$ 时，每次 `put` 新键都会淘汰唯一的那个节点。
- `put` 更新已有的键也算一次使用，要移到头。
- `get` 没命中时不改链表顺序。
- 先 `put` 满、再 `get`、再 `put` 时，淘汰的是当前的尾巴，它不一定是插入顺序里最早的那个。

## 追问

**改成 LFU（LC 460）怎么做？**
在键到节点的哈希之外，再按频次分层，每个频次一条双向链表，同一频次内部仍按 LRU 排，尾巴最久。节点多记一个 `freq`。`get`/`put` 命中时，把节点从旧频次的链表摘下，`freq+1` 后插到新一层的头部；如果旧层空了而且它正好是 `min_freq`，`min_freq` 加一。插入新键时频次为 $1$，`min_freq=1`；满了就淘汰 `min_freq` 这一层的尾巴，并同步删哈希。这里同样要双向链表才能 $O(1)$ 删中间节点，整体均摊 $O(1)$。容量为 $0$ 时直接忽略 `put`。

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

**要线程安全或者分布式呢？**
单机就加一把锁（或者读写锁），把「查哈希 + 搬节点」整个包住，否则两个线程同时 `get` 会把链表指针拧乱，只锁哈希不锁链表也一样会乱。分布式就没法靠一台机器上的双链表了，要用一致性哈希把键分到各个分片，每片各自做 LRU，再加 TTL / 版本号处理过期和并发写。跨分片没有全局的「最久未用」，只能近似。回答时我会把单机 $O(1)$ 和分布式分片分开讲。
