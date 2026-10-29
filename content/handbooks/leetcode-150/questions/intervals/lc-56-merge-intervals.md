---
id: lc-56-merge-intervals
section: intervals
order: 2
level: S
title: LC 56 · 合并区间
quick: 先按起点排序，再扫一遍：下一个区间能和答案末段重叠（含端点相接）就把 `end` 扩到更大，否则新开一段。时间 $O(n\log n)$。
tags:
  - Intervals
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 56. 合并区间
    url: 'https://leetcode.cn/problems/merge-intervals/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一组闭区间，把所有互相重叠的区间合并，返回覆盖范围完全相同、彼此不再重叠的区间集合。闭区间包含两端点，因此 `[1,4]` 与 `[4,5]` 也应合并。若若干区间通过重叠连成一片，需要合并为一个整体。

### 输入与输出

实现 `merge(intervals: List[List[int]]) -> List[List[int]]`。每个输入、输出区间都用 `[start,end]` 表示。输入顺序没有排序保证；结果不应遗漏或新增被覆盖的点。

### 约束

- `1 <= len(intervals) <= 10^4`，每个区间恰有两个端点。
- `0 <= start <= end <= 10^4`。

### 示例

```text
输入：intervals = [[1,3],[2,6],[8,10],[15,18]]
输出：[[1,6],[8,10],[15,18]]
```

前两个区间合并为 `[1,6]`；后两个区间与它不重叠，分别保留。

## 解题思路与参考答案

## 题意

给若干闭区间 `[start, end]`，把所有重叠（包括端点相接）的合并，返回互不相交的区间列表。

## 思路

我会先按起点升序排序。不排序的话，左边一个大区间可能罩住右边好几个，没法一遍线性扫完。排好以后维护答案里的最后一段 `[l, r]`：下一个 `[s, e]` 如果 $s\le r$，说明重叠或相接，令 $r=\max(r,e)$；否则把 `[s, e]` 作为新的一段追加进去。

拿 `[[1,3],[2,6],[8,10],[15,18]]` 来说，`[2,6]` 的起点 2 不超过 3，和 `[1,3]` 合成 `[1,6]`；`[8,10]` 起点 8 大于 6，另起一段；`[15,18]` 同样各留一段。端点相等也要合并，`[1,4]` 和 `[4,5]` 合成 `[1,5]`。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
assert merge([[1, 4], [4, 5]]) == [[1, 5]]
assert merge([[1, 4], [0, 4]]) == [[0, 4]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n\log n)$，额外空间 $O(n)$（排序与答案）。合并本身是线性的。

## Edge Cases

只有一个区间时循环不进，原样返回。完全包含时 `end` 取 `max`，里面那个被吞掉。只在端点相接时 $start \le res[-1][1]$ 成立，合成一段。起点乱序时必须先按起点排序，否则没法线性扫。零宽度区间和负坐标都不影响比较规则。

## 追问

**开区间、端点相接不合并呢？**
改一个符号就行：重叠判定从 $start \le res[-1][1]$ 改成 $start \lt res[-1][1]$。`[1,4)` 和 `[4,5)` 不相交，应该分成两段。其余照旧，按起点排序、维护答案末段的 `end`。先问清开闭再改符号，时间仍是 $O(n\log n)$。`max` 别漏掉，开区间下真正相交时，后一段仍然可能更长。

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

**插入一段再合并（LC 57）呢？**
原列表已经按起点排好且互不重叠时，不用整表重排，一次扫描分三段就行：$end \lt new.start$ 的原样抄到左边；和新区间有重叠的，用它们把新区间的左右端扩开；$start \gt new.end$ 的抄到右边。中间那段扩完只插入一次。新区间也可能落在最前、最后，或者把中间若干段全吃掉。时间 $O(n)$。单独一张卡 `lc-57-insert-interval`。

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
