---
id: lc-274-h-index
section: array-string
order: 11
level: A
title: LC 274 · H 指数
quick: "升序排序后从左往右找：位置 $i$ 往右还有 $n-i$ 篇，若 `citations[i] >= n-i`，$n-i$ 就是合法的 $h$，第一个满足的就是最大的。时间 $O(n\\log n)$，额外空间 $O(1)$；桶计数可以做到 $O(n)$ 时间、$O(n)$ 空间。"
tags:
  - Array
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 274. H 指数
    url: https://leetcode.cn/problems/h-index/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

一位研究者的每篇论文都有一个非负引用次数。H 指数定义为最大的非负整数 h，使研究者至少有 h 篇论文各被引用不少于 h 次。给出全部论文的引用次数，返回其 H 指数。

### 输入与输出

实现 `hIndex(citations) -> int`。`citations[i]` 是第 i 篇论文的引用次数，输入没有预先排序。只返回最大的 h，不返回论文集合。

### 约束与约定

- `1 <= len(citations) <= 5000`。
- `0 <= citations[i] <= 1000`。

### 示例

```text
输入：citations = [3,0,6,1,5]
输出：3
```

有 3 篇论文的引用次数分别达到至少 3 次，但没有 4 篇各达到至少 4 次，所以答案为 3。

[官方原题与完整题面](https://leetcode.com/problems/h-index/description/)。

## 解题思路与参考答案

## 题意

`citations[i]` 是第 $i$ 篇论文被引次数。H 指数是最大的 $h$，使得至少有 $h$ 篇论文的引用 $\ge h$。

## 思路

我先排序，排好之后「至少 $h$ 篇引用 $\ge h$」可以直接按位置判断。升序排好后从左往右看，位置 $i$ 往右（含自己）还剩 $n-i$ 篇，如果 `citations[i] >= n-i`，那 $n-i$ 就是合法的 $h$。$n-i$ 是递减的，所以第一个满足的就是最大的。

拿 `[3, 0, 6, 1, 5]` 走一遍：排序得 `[0, 1, 3, 5, 6]`；$i=0$ 时 $0 \lt 5$，$i=1$ 时 $1 \lt 4$，$i=2$ 时 $3 \ge 3$，答案是 $3$。

也可以用桶计数：引用超过 $n$ 的都计入桶 $n$，从高往低累加篇数，累加到 $\ge h$ 时返回。排序好讲，计数是 $O(n)$ 的优化。

## 参考代码

```python
from typing import List


def hIndex(citations: List[int]) -> int:
    citations.sort()
    n = len(citations)
    for i, c in enumerate(citations):
        if c >= n - i:
            return n - i
    return 0


if __name__ == "__main__":
    assert hIndex([3, 0, 6, 1, 5]) == 3
    assert hIndex([1, 3, 1]) == 1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
assert hIndex([3, 0, 6, 1, 5]) == 3
assert hIndex([1, 3, 1]) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

排序 $O(n\log n)$ 时间、$O(1)$ 或 $O(n)$ 空间（取决于是否原地）。计数排序做法时间 $O(n)$。

## 边界

全是 $0$ 时没有一篇引用 $\ge 1$，H 是 $0$。只有一篇且引用很大，最多也只有 $1$ 篇，H 只能是 $1$。每篇引用都 $\ge n$ 时，全部 $n$ 篇都满足，H 是 $n$。

## 追问

**引用次数远大于 $n$ 怎么办？**
把引用截断到 $n$ 就行。H 指数的定义决定了 $h$ 最大就是论文篇数 $n$，一篇引用 $10^9$ 的论文也只贡献「有一篇 $\ge n$」。所以计数做法写 `bucket[min(c, n)] += 1`，再从 $h=n$ 往下累加「至少 $h$ 篇」，第一次累加 $\ge h$ 就是答案。时间 $O(n)$，额外空间 $O(n)$。桶别开成最大引用值那么大；也别从低往高扫，那样拿到的是最小的合法 $h$。排序做法不受这个影响，只是变成 $O(n\log n)$。

```python
def hIndex_count(citations):
    n = len(citations)
    bucket = [0] * (n + 1)
    for c in citations:
        bucket[min(c, n)] += 1
    acc = 0
    for h in range(n, -1, -1):
        acc += bucket[h]
        if acc >= h:
            return h
    return 0
```

**数组已经有序呢？论文流式到达呢？**
已经升序（LC 275）就不用再排序，直接在 $[0,n]$ 上二分 $h$，判定条件是 `citations[n-h] >= h`，也就是最弱的那篇仍 $\ge h$。这个条件单调，时间 $O(\log n)$，额外空间 $O(1)$；对无序数组直接二分会错。流式到达时，每来一篇 H 最多加 $1$，可以维护一个小根堆：新引用 $\gt$ 堆大小就入堆，再弹出堆顶 $\le$ 堆大小的元素，堆大小就是当前 H。每篇入堆、出堆各至多一次，总共 $O(n\log n)$，不需要每来一篇就把全部论文重新排序。

```python
def hIndex_sorted(citations):
    n = len(citations)
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if citations[n - mid] >= mid:
            lo = mid
        else:
            hi = mid - 1
    return lo


import heapq


class HIndexStream:
    def __init__(self):
        self.heap = []

    def add(self, c):
        if c > len(self.heap):
            heapq.heappush(self.heap, c)
        while self.heap and self.heap[0] <= len(self.heap) - 1:
            heapq.heappop(self.heap)
        return len(self.heap)
```
