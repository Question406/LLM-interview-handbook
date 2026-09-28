---
id: lc-452-minimum-number-of-arrows-to-burst-balloons
section: intervals
order: 2
level: A
title: LC 452 · 用最少数量的箭引爆气球
quick: >-
  按气球右端点排序。一支箭钉在当前组第一个气球的终点；下一个起点仍 $\le$ 该终点就同箭，否则再射一支。时间
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
  - title: 452. Minimum Number of Arrows to Burst Balloons
    url: https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

每个气球是 x 轴上的闭区间 `[start, end]`。在 $x$ 处竖直射一支箭，能射爆所有满足 $start\le x\le end$ 的气球，箭穿过后继续飞。求射爆全部气球的最少箭数。$1\le n\le 10^5$，坐标在 32 位有符号整数范围内。

## 思路

贪心：按终点升序。第一支箭射在第一个气球的终点，这是能射到它的最右位置，能顺带打掉所有起点不超过该终点的气球。遇到起点大于当前箭位的气球，这支箭覆盖不到，再射一支钉在它的终点。

按终点排：结束最早的气球决定了这支箭最晚必须落在哪，把箭放在这个最晚位置才能给后面留最大重叠。端点相等也能同箭（闭区间），所以换箭条件是 $start\gt end$。

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
    assert findMinArrowShots([[1, 5]]) == 1
    assert findMinArrowShots([[-2**31, 2**31 - 1], [0, 0]]) == 1
    print("ok")
```

## 复杂度

时间 $O(n\log n)$，额外空间 $O(1)$（不计排序）。贪心扫描线性。

## 边界

- 一个气球：直接返回 $1$。
- 只在端点相接：闭区间 `[1,2]` 与 `[2,3]` 可同箭，代码用 $start\gt end$ 才换箭。
- 极端坐标：Java / C++ 里按 `a[1] - b[1]` 排序会溢出，要用比较函数；Python 没这个问题。
- 零宽度气球（`start == end`）：仍占一个点，可被钉在该点的箭射中。

## 追问

- **改成开区间？** 端点相接不再共用一支箭。把判断从 $start\gt end$ 改成 $start\ge end$，其余不变。先确认题面是闭还是开，这块容易栽在符号上。

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

- **和无重叠区间（`lc-435-non-overlapping-intervals`）什么关系？** 同一套按终点贪心。每支箭对应一组重叠气球，组数就是闭区间意义下的最多互不相交气球数；LC 435 求的是 $n$ 减去最多保留数，而且端点相接不算重叠，保留条件是 $s\ge end$。别和合并区间搞混：合并要并集，这题要点覆盖。
