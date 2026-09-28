---
id: lc-435-non-overlapping-intervals
section: intervals
order: 1
level: S
title: LC 435 · 无重叠区间
quick: >-
  等价于「最多保留多少个互不重叠区间」。按右端点升序，能接上就保留并更新结束位置，答案是 $n-\textit{keep}$。时间
  $O(n\log n)$，额外空间 $O(1)$（不计排序）。
tags:
  - Greedy
  - Intervals
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 435. Non-overlapping Intervals
    url: https://leetcode.com/problems/non-overlapping-intervals/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

区间数组 `intervals[i] = [start, end]`，求最少移除多少个区间，使剩下的区间两两不重叠。端点相接（如 `[1,2]` 和 `[2,3]`）不算重叠。$1\le n\le 10^5$，坐标在 $[-5\times 10^4, 5\times 10^4]$。

## 思路

最少删除 $=n-$ 最多保留。最多保留互不重叠区间就是经典活动选择：按右端点升序，记当前已选区间的结束位置 `end`；下一个区间起点 $\ge$ `end` 就保留并把 `end` 更新成它的终点，否则丢掉。

为什么按终点：在所有可选的区间里挑结束最早的，给后面留的空间最大。用交换论证：任何最优解的第一个区间都能换成结束最早的那个而不产生冲突，依次归纳即可。按起点排序再贪心会被一个很长的早起区间坑住，比如 `[1,100]` 挡住后面一串短区间。暴力枚举子集是指数级；按起点排序做 $O(n^2)$ 的 LIS 式 DP 能对，但会超时。

## 参考代码

```python
from typing import List


def eraseOverlapIntervals(intervals: List[List[int]]) -> int:
    intervals.sort(key=lambda x: x[1])
    keep = 0
    end = float("-inf")
    for s, e in intervals:
        if s >= end:
            keep += 1
            end = e
    return len(intervals) - keep


if __name__ == "__main__":
    assert eraseOverlapIntervals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
    assert eraseOverlapIntervals([[1, 2], [1, 2], [1, 2]]) == 2
    assert eraseOverlapIntervals([[1, 2], [2, 3]]) == 0
    assert eraseOverlapIntervals([[1, 100], [11, 22], [1, 11], [2, 12]]) == 2
    assert eraseOverlapIntervals([[0, 1]]) == 0
    assert eraseOverlapIntervals([[-5, -1], [-3, 2], [0, 4]]) == 1
    print("ok")
```

## 复杂度

时间 $O(n\log n)$，排序为主，扫描线性。额外空间 $O(1)$，不计排序。

## 边界

- 端点相接：用 $s\ge end$ 判断，`[1,2]`、`[2,3]` 都保留；写成 $s\gt end$ 会多删。
- 完全相同的区间：只能留一个，其余全删。
- 负坐标：`end` 初值用 $-\infty$，不要用 $0$ 或 $-1$。

## 追问

- **和射气球（`lc-452-minimum-number-of-arrows-to-burst-balloons`）什么关系？** 同一套按终点贪心。气球是闭区间，端点相接也能被同一支箭射穿，所以换箭条件是 $s\gt end$；本题端点相接不算重叠，保留条件是 $s\ge end$。箭数等于闭区间意义下的最多不相交区间数。

- **要返回具体删掉哪些区间？** 排序时带上原下标，贪心时没被保留的就是要删的。

```python
def eraseOverlapIntervalsWhich(intervals):
    order = sorted(range(len(intervals)), key=lambda i: intervals[i][1])
    end, removed = float("-inf"), []
    for i in order:
        s, e = intervals[i]
        if s >= end:
            end = e
        else:
            removed.append(i)
    return removed
```
