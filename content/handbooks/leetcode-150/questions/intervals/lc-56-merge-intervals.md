---
id: lc-56-merge-intervals
section: intervals
order: 2
level: S
title: LC 56 · 合并区间
quick: >-
  按起点排序。扫下一个区间：能与当前末段重叠则把 `end` 扩到更大，否则新开一段。时间
  $O(n\log n)$。
tags:
  - Intervals
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 56. 合并区间
    url: https://leetcode.cn/problems/merge-intervals/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

若干闭区间 `[start, end]`，把所有重叠（含端点相接）的合并，返回互不相交的区间列表。

## 思路

不排序无法线性扫：左边一个大区间可能罩住右边。先按起点升序。维护答案末段 `[l, r]`：下一个 `[s, e]` 若 $s\le r$，重叠或相接，令 $r=\max(r,e)$；否则把 `[s, e]` 追加为新段。

`[1,3]` 与 `[2,6]` 合成 `[1,6]`；`[8,10]`、`[15,18]` 各留。端点相等也要合并。

## 参考代码

```python
from typing import List


def merge(intervals: List[List[int]]) -> List[List[int]]:
    intervals.sort()
    res = [intervals[0][:]]
    for start, end in intervals[1:]:
        if start <= res[-1][1]:
            res[-1][1] = max(res[-1][1], end)
        else:
            res.append([start, end])
    return res


if __name__ == "__main__":
    assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert merge([[1, 4], [4, 5]]) == [[1, 5]]
    assert merge([[1, 4], [0, 4]]) == [[0, 4]]
    print("ok")
```

## 复杂度

时间 $O(n\log n)$，额外空间 $O(n)$（排序与答案）。合并本身线性。

## 边界

- 单区间：循环不进，原样返回。
- 完全包含：`end` 取 `max`，内层被吞掉。
- 只在端点相接：$start \le res[-1][1]$ 为真，合并成一段。
- 乱序起点：必须先按起点排序，否则无法线性扫。
- 零宽度、负坐标：比较规则不变。

## 追问

- **开区间，相接端点不合并？** 把重叠判定从 $start \le res[-1][1]$ 改成 $start \lt res[-1][1]$。`[1,4)` 与 `[4,5)` 不相交，应分两段。其余仍按起点排序、维护答案末段的 `end`。面试先问清开闭，再改一个符号。时间仍 $O(n\log n)$。不要漏掉 `max`：即使开区间，真正相交时仍可能后段更长。

```python
def mergeOpen(intervals):
    intervals.sort()
    res = [intervals[0][:]]
    for start, end in intervals[1:]:
        if start < res[-1][1]:
            res[-1][1] = max(res[-1][1], end)
        else:
            res.append([start, end])
    return res
```

- **插入一段再合并（LC 57）？** 原表已按起点排序且互不重叠时不必整表重排。一次扫描分三段：$end \lt new.start$ 的原样抄到左边；与新区间有重叠的把左右端扩掉；$start \gt new.end$ 的抄到右边。中间那段扩完只插入一次。新区间也可能落在最前、最后，或把中间若干段全吃掉。时间 $O(n)$。独立卡见 `lc-57-insert-interval`。

```python
def insert(intervals, newInterval):
    res, i, n = [], 0, len(intervals)
    ns, ne = newInterval
    while i < n and intervals[i][1] < ns:
        res.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= ne:
        ns = min(ns, intervals[i][0])
        ne = max(ne, intervals[i][1])
        i += 1
    res.append([ns, ne])
    res.extend(intervals[i:])
    return res
```
