---
id: lc-452-minimum-number-of-arrows-to-burst-balloons
section: intervals
order: 4
level: A
title: LC 452 · 用最少数量的箭引爆气球
quick: >-
  按气球右端点排序。一支箭钉在当前段的终点；下一个起点仍 $\le$ 该终点就同箭，否则再射一支。时间
  $O(n\log n)$。
tags:
  - Greedy
  - Intervals
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 452. 用最少数量的箭引爆气球
    url: https://leetcode.cn/problems/minimum-number-of-arrows-to-burst-balloons/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

每个气球是闭区间 `[start, end]`。一支箭在整数 $x$ 能射爆所有覆盖 $x$ 的气球。求射爆全部气球的最少箭数。

## 思路

贪心：先按终点升序。第一支箭射在第一个气球的终点，能顺带打掉所有起点不超过该终点的气球。遇到起点大于当前箭位置的气球，覆盖不上，再射一支钉在它的终点。

按终点排而不是按起点：尽早结束的气球决定「这支箭最晚必须落在哪」，才能给后面留最大重叠。端点相等也能同箭（闭区间）。

## 参考代码

```python
from typing import List


def findMinArrowShots(points: List[List[int]]) -> int:
    points.sort(key=lambda p: p[1])
    arrows = 1
    end = points[0][1]
    for start, finish in points[1:]:
        if start > end:
            arrows += 1
            end = finish
    return arrows


if __name__ == "__main__":
    assert findMinArrowShots([[10, 16], [2, 8], [1, 6], [7, 12]]) == 2
    assert findMinArrowShots([[1, 2], [3, 4], [5, 6], [7, 8]]) == 4
    assert findMinArrowShots([[1, 2], [2, 3], [3, 4], [4, 5]]) == 2
    print("ok")
```

## 复杂度

时间 $O(n\log n)$，额外空间 $O(1)$（不计排序）。贪心扫描线性。

## 边界

- 一个气球：排序后直接返回 $1$。
- 全部重叠：全程 $start\le end$，只射一支。
- 只在端点相接：闭区间 `[1,2]` 与 `[2,3]` 可同箭，代码用 $start \gt end$ 才换箭。
- 负坐标：比较与排序都合法，不必平移。
- 零宽度气球（`start == end`）：仍占一个点，可被钉在该点的箭射中。

## 追问

- **改成开区间？** 端点相接不再共用一支箭。把判断从 $start \gt end$ 改成 $start \ge end$：当前气球起点已经不小于箭位，覆盖不到。其余仍按右端点升序，箭钉在当前组的终点。时间 $O(n\log n)$ 不变。先确认题面是闭还是开，这块容易栽在符号上。别同时改排序键，仍按终点排。

```python
def findMinArrowShotsOpen(points):
    points.sort(key=lambda p: p[1])
    arrows, end = 1, points[0][1]
    for start, finish in points[1:]:
        if start >= end:
            arrows += 1
            end = finish
    return arrows
```

- **最多不重叠区间（活动选择）？** 同一套按终点贪心：右端点升序后，能选就选。这题「最少箭」在闭区间下恰好等于「最多互不重叠气球数」。每支箭钉在一组重叠的最右端，下一支必须开新组，组数就是最大不相交子集大小。活动选择要的是保留数 `keep`；若问删多少才能不重叠（LC 435），答案是 $n-\textit{keep}$。注意判定符号：活动选择里端点相接通常允许（$s \ge last\_end$ 可保留），而这题闭区间相接算同一箭（$s \gt end$ 才换箭）。别和合并区间搞混：合并要并集，这题要点覆盖。合并卡见 `lc-56-merge-intervals`。

```python
def maxNonOverlap(intervals):
    intervals.sort(key=lambda x: x[1])
    keep, end = 0, float("-inf")
    for s, e in intervals:
        if s >= end:
            keep += 1
            end = e
    return keep
```
