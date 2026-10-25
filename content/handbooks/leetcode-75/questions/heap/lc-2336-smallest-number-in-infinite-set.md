---
id: lc-2336-smallest-number-in-infinite-set
section: heap
order: 2
level: A
title: LC 2336 · 无限集中的最小数字
quick: "用指针 `cur` 表示「从 `cur` 起的所有正整数都还在集合里」，再用小根堆加哈希集合存被加回来、比 `cur` 小的数。弹出时堆非空取堆顶，否则取 `cur`。两个操作都是 $O(\\log m)$，$m$ 是堆大小。"
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

## 题目描述

维护一个最初包含所有正整数 1、2、3……的集合，实现移除最小值和把正整数加回集合的操作。加回已经存在的数不应产生第二份副本；加回先前移除的数后，它可以再次成为最小值。

### 输入与输出

实现 `SmallestInfiniteSet()`；`popSmallest() -> int` 移除并返回当前集合的最小数；`addBack(num) -> None` 在 num 缺失时重新加入它。集合不允许重复元素，且 popSmallest 总能返回一个数。

### 约束与约定

- `1 <= num <= 1000`。
- popSmallest 与 addBack 合计调用不超过 1000 次。

### 示例

```text
输入：["SmallestInfiniteSet", "addBack", "popSmallest", "popSmallest", "popSmallest", "addBack", "popSmallest", "popSmallest", "popSmallest"]
[[], [2], [], [], [], [1], [], [], []]
输出：[null, null, 1, 2, 3, null, 1, 4, 5]
```

示例首先 addBack(2) 不改变初始集合；连续移除 1、2、3 后加回 1，下一次最小值又是 1。输出中的 null 代表构造器或无返回值的方法。

[官方原题与完整题面](https://leetcode.com/problems/smallest-number-in-infinite-set/description/)。

## 解题思路与参考答案

## 题意

集合一开始包含所有正整数 $1, 2, 3, \dots$。实现 `SmallestInfiniteSet`：

- `popSmallest()`：移除并返回集合里最小的数。
- `addBack(num)`：若 `num` 不在集合里，把它加回去；已在则什么都不做。

$1\le$ `num` $\le 1000$，总调用次数不超过 $1000$。

## 思路

我把集合拆成两部分来存：一段无限的后缀 $[cur, \infty)$ 全在集合里，用一个指针表示；再加上若干个比 `cur` 小、被 `addBack` 放回来的零散数，放进小根堆。

另外用一个 `set` 记录堆里有哪些数，防止重复加入。堆里的数都比 `cur` 小，所以 `popSmallest` 时堆非空就弹堆顶，否则返回 `cur` 并让 `cur` 加一。`addBack(num)` 只在 `num` 小于 `cur` 且不在堆里时才入堆；`num` 大于等于 `cur` 说明它本来就在后缀里。

拿测试里的第一段走一遍：先 `addBack(2)`，这时 `cur` 是 1，2 本来就在后缀里，忽略。连弹三次得到 1、2、3，`cur` 变成 4。再 `addBack(1)`，1 比 4 小，入堆。下一次弹出先拿堆顶 1，再往后是 4、5。

数据范围小，也可以直接开一个长度 $1001$ 的布尔数组线性找最小，但每次 `pop` 是 $O(C)$，而且依赖值域上限，面试里我讲堆的版本。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
s = SmallestInfiniteSet()
s.addBack(2)
assert s.popSmallest() == 1
assert s.popSmallest() == 2
assert s.popSmallest() == 3
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

`popSmallest` 和 `addBack` 都是 $O(\log m)$，$m$ 是堆里的数的个数，不会超过已经弹出过的数的个数。额外空间 $O(m)$。

## 边界

加回一个从没弹出过的数（`num` 大于等于 `cur`）时，它本来就在集合里，忽略。

同一个数连续 `addBack` 两次，靠 `in_heap` 去重，否则会被弹出两次。

加回的数被弹出后再加回，`remove` 之后集合里已经没有它，可以正常再入堆。

## 追问

**有序集合怎么写？**
语言里有平衡树的话（Java `TreeSet`、C++ `set`），直接用它替代「堆加哈希集合」，自带去重和取最小。Python 没有内置平衡树，堆加 `set` 是最直接的替代。

**要支持任意删除 `remove(num)` 呢？**
在堆上做懒删除：`remove` 只在 `in_heap` 里删掉，`popSmallest` 时先把堆顶那些已经不在 `in_heap` 里的数弹掉。后缀部分的删除需要另一个「已删除且大于等于 `cur`」的集合，`cur` 往前走时跳过它们。
