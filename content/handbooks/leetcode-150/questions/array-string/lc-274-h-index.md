---
id: lc-274-h-index
section: array-string
order: 11
level: A
title: LC 274 · H 指数
quick: >-
  升序排序后找最大 $h$，使 `citations[i] >= n-i`（至少 $h$ 篇 $\ge h$）。时间
  $O(n\log n)$，额外空间 $O(1)$ 或计数 $O(n)$。
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

## 题意

`citations[i]` 是第 $i$ 篇论文被引次数。H 指数是最大的 $h$，使得至少有 $h$ 篇论文的引用 $\ge h$。

## 思路

升序排序后，从左往右看：右边还剩 $n-i$ 篇，若 `citations[i] >= n-i`，则 $n-i$ 是合法 $h$。取满足条件的最大者（第一个满足的就是最大，因为 $n-i$ 递减）。

也可用桶计数：引用超过 $n$ 的都打进桶 $n$，从高往低累加篇数，累加 $\ge h$ 时返回。排序好讲，计数是 $O(n)$ 优化。

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

## 复杂度

排序 $O(n\log n)$ 时间、$O(1)$ 或 $O(n)$ 空间（取决于是否原地）。计数排序做法时间 $O(n)$。

## 边界

- 全是 $0$：没有任何一篇引用 $\ge 1$，H 为 $0$。
- 只有一篇且引用很大：最多 $1$ 篇，H 只能是 $1$。
- 每篇引用都 $\ge n$：全部 $n$ 篇都 $\ge n$，H 为 $n$。

## 追问

- **引用次数远大于 $n$ 怎么办？** H 指数的定义决定了 $h$ 最大就是论文篇数 $n$，一篇引用 $10^9$ 也只贡献「有一篇 $\ge n$」。所以计数做法把引用截断到 $n$：`bucket[min(c, n)] += 1`，再从 $h=n$ 往下累加「至少 $h$ 篇」。第一次累加 $\ge h$ 就是答案。时间 $O(n)$，额外空间 $O(n)$。这块容易栽：桶开成「最大引用值」那么大，以及从低往高扫会拿到最小合法 $h$ 而不是最大。排序做法不受这个影响，但变成 $O(n\log n)$。

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

- **论文流式到达？数组已经有序呢？** 已经升序（LC 275）时不必再排序：在 $[0,n]$ 上二分 $h$，判定 `citations[n-h] >= h`（最弱的那篇仍 $\ge h$）。单调，时间 $O(\log n)$，额外空间 $O(1)$。对无序数组直接二分会错。流式到达时，每来一篇 H 最多加 $1$。维护小根堆：新引用若 $\gt$ 堆大小则入堆，再弹出堆顶 $\le$ 堆大小的，堆大小就是当前 H；每篇入堆、出堆各至多一次，总共 $O(n\log n)$。不要每来一篇就全局重排。

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
