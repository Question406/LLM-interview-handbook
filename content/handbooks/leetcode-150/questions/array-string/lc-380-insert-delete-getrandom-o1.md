---
id: lc-380-insert-delete-getrandom-o1
section: array-string
order: 12
level: A
title: LC 380 · O(1) 时间插入、删除和获取随机元素
quick: >-
  哈希表存「值 $\to$ 下标」，数组存元素。删除时把末尾元素换到被删位置再 `pop`。`getRandom` 对数组均匀抽样。均摊
  $O(1)$。
tags:
  - Hash
  - Design
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 380. O(1) 时间插入、删除和获取随机元素
    url: https://leetcode.cn/problems/insert-delete-getrandom-o1/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

实现 `RandomizedSet`：`insert` / `remove` 成功返回 `true`（值已在 / 不在则失败），`getRandom` 等概率返回当前集合中任一元素。均摊 $O(1)$。

## 思路

只靠哈希表无法 $O(1)$ 均匀随机（遍历键是 $O(n)$）。数组提供下标随机，哈希提供值到下标。插入：不存在则追加到数组并记索引。删除时把数组末尾元素搬到被删下标，更新哈希，再 `pop` 末尾，避免中间 `pop` 变成 $O(n)$。删的就是末尾时直接 `pop`。

## 参考代码

```python
import random
from typing import Dict, List


class RandomizedSet:
    def __init__(self) -> None:
        self.idx: Dict[int, int] = {}
        self.arr: List[int] = []

    def insert(self, val: int) -> bool:
        if val in self.idx:
            return False
        self.idx[val] = len(self.arr)
        self.arr.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.idx:
            return False
        i = self.idx[val]
        last = self.arr[-1]
        self.arr[i] = last
        self.idx[last] = i
        self.arr.pop()
        del self.idx[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.arr)


if __name__ == "__main__":
    s = RandomizedSet()
    assert s.insert(1) is True
    assert s.remove(2) is False
    assert s.insert(2) is True
    assert s.getRandom() in (1, 2)
    assert s.remove(1) is True
    assert s.insert(2) is False
    assert s.getRandom() == 2
    print("ok")
```

## 复杂度

`insert` / `remove` / `getRandom` 均摊 $O(1)$ 时间。空间 $O(n)$。

## 边界

- 删除唯一元素：换尾后数组变空，哈希清空，随后 `getRandom` 不能再调。
- 删除的正好是末尾：换尾是自身赋值，直接 `pop` 并删哈希即可。
- 插入已存在值：哈希命中，返回 `false`，数组长度不变。

## 追问

- **允许重复呢（LC 381）？** 值可以出现多次，`getRandom` 要按「出现次数」均匀，所以数组里必须存重复元素。哈希改成值 $\to$ 下标集合。`insert` 总是追加，返回「此前是否不存在」。`remove` 只删一次：从该值的下标集合里拿出一个 `i`，把末尾元素搬到 `i`，更新末尾值的下标集合（加 `i`、丢掉旧尾部下标），再 `pop`。删的是最后一个下标时，加和删抵消，不要特判错。均摊仍 $O(1)$（集合增删），空间 $O(n)$。这块容易栽：搬尾时没改哈希，以及空集合没从哈希里删掉导致误判还在。

```python
import random


class RandomizedCollection:
    def __init__(self):
        self.idx = {}
        self.arr = []

    def insert(self, val):
        self.idx.setdefault(val, set()).add(len(self.arr))
        self.arr.append(val)
        return len(self.idx[val]) == 1

    def remove(self, val):
        if val not in self.idx or not self.idx[val]:
            return False
        i = self.idx[val].pop()
        last = self.arr[-1]
        self.arr[i] = last
        self.idx[last].add(i)
        self.idx[last].discard(len(self.arr) - 1)
        self.arr.pop()
        if not self.idx[val]:
            del self.idx[val]
        return True

    def getRandom(self):
        return random.choice(self.arr)
```

- **并发或要持久化？** 三个方法共用同一对数组和哈希，没有锁，不是线程安全。两个线程同时 `insert` 可能写到同一尾部下标；`remove` 的换尾和 `getRandom` 并发会抽到半删除状态。要并发就给三个方法加同一把互斥锁，均摊时间仍 $O(1)$，但吞吐受锁限制；读写锁收益不大，因为 `getRandom` 也依赖长度和内容。持久化必须同时快照 `arr` 和 `idx`，只存数组不够，下标会随删除变化。随机性来自 `random.choice`，单测应注入 RNG。不要用遍历哈希键当随机：既不是均匀，也是 $O(n)$。
