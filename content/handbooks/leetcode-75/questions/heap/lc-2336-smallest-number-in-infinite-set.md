---
id: lc-2336-smallest-number-in-infinite-set
section: heap
order: 2
level: A
title: LC 2336 · 无限集中的最小数字
quick: >-
  用指针 `cur` 表示「从 `cur` 起的所有正整数都还在集合里」，再用小根堆加哈希集合存被加回来的、比 `cur`
  小的数。弹出时堆非空取堆顶，否则取 `cur`。两个操作都是 $O(\log m)$，$m$ 是堆大小。
tags:
  - Heap
  - Design
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2336. Smallest Number in Infinite Set
    url: https://leetcode.com/problems/smallest-number-in-infinite-set/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

集合一开始包含所有正整数 $1, 2, 3, \dots$。实现 `SmallestInfiniteSet`：

- `popSmallest()`：移除并返回集合里最小的数。
- `addBack(num)`：若 `num` 不在集合里，把它加回去；已在则什么都不做。

$1\le$ `num` $\le 1000$，总调用次数不超过 $1000$。

## 思路

集合的状态可以拆成两部分：一段无限的后缀 $[cur, \infty)$ 全部在集合里，加上若干个比 `cur` 小、被 `addBack` 放回来的零散数。

零散数放小根堆，另用一个 `set` 记录堆里有哪些，防止重复加入。堆里的数都小于 `cur`，所以 `popSmallest` 时堆非空就弹堆顶，否则返回 `cur` 并让 `cur` 加一。`addBack(num)` 只有在 `num` 小于 `cur` 且不在堆里时才入堆；`num` 大于等于 `cur` 说明它本来就在后缀里。

也可以因为数据范围小直接开一个长度 $1001$ 的布尔数组线性找最小，但每次 `pop` 是 $O(C)$，而且依赖值域上限，面试我讲堆的版本。

## 参考代码

```python
import heapq
from typing import List, Set


class SmallestInfiniteSet:
    def __init__(self) -> None:
        self.cur = 1
        self.heap: List[int] = []
        self.in_heap: Set[int] = set()

    def popSmallest(self) -> int:
        if self.heap:
            x = heapq.heappop(self.heap)
            self.in_heap.remove(x)
            return x
        self.cur += 1
        return self.cur - 1

    def addBack(self, num: int) -> None:
        if num < self.cur and num not in self.in_heap:
            heapq.heappush(self.heap, num)
            self.in_heap.add(num)


if __name__ == "__main__":
    s = SmallestInfiniteSet()
    s.addBack(2)
    assert s.popSmallest() == 1
    assert s.popSmallest() == 2
    assert s.popSmallest() == 3
    s.addBack(1)
    assert s.popSmallest() == 1
    assert s.popSmallest() == 4
    assert s.popSmallest() == 5

    s = SmallestInfiniteSet()
    s.addBack(5)
    assert s.popSmallest() == 1
    assert s.popSmallest() == 2
    s.addBack(1)
    s.addBack(1)
    s.addBack(2)
    assert s.popSmallest() == 1
    assert s.popSmallest() == 2
    assert s.popSmallest() == 3
    print("ok")
```

## 复杂度

`popSmallest` 与 `addBack` 都是 $O(\log m)$，$m$ 是堆里的数的个数，$m$ 不超过已弹出过的数的个数。额外空间 $O(m)$。

## 边界

- 加回一个从未弹出的数（`num` 大于等于 `cur`）：它本来就在集合里，忽略。
- 同一个数连续 `addBack` 两次：靠 `in_heap` 去重，否则会被弹出两次。
- 加回的数弹出后再次加回：`remove` 后集合里没有它，可以正常再入堆。

## 追问

- **有序集合写法？** 如果语言有平衡树（Java `TreeSet`、C++ `set`），用它替代「堆加哈希集合」，自带去重和取最小。Python 没有内置平衡树，堆加 `set` 是最直接的替代。
- **要支持任意删除 `remove(num)`？** 在堆上做懒删除：`remove` 只在 `in_heap` 里删掉，`popSmallest` 时先把堆顶里已不在 `in_heap` 的数弹掉。对后缀部分的删除需要另一个「已删除且大于等于 `cur`」的集合，`cur` 前进时跳过它们。
