---
id: lc-435-non-overlapping-intervals
section: intervals
order: 1
level: S
title: LC 435 · 无重叠区间
quick: >-
  最少删除等于 $n$ 减去最多能保留的互不重叠区间数。按右端点升序贪心，起点不早于当前结束位置就保留并更新结束位置，答案是
  $n-\textit{keep}$。时间 $O(n\log n)$，额外空间 $O(1)$（不计排序）。
tags:
  - Greedy
  - Intervals
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 435. Non-overlapping Intervals
    url: 'https://leetcode.com/problems/non-overlapping-intervals/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定若干区间 `intervals[i]=[start,end]`，删除尽量少的区间，使剩余区间两两不重叠。端点相接不算重叠，例如 `[1,2]` 和 `[2,3]` 可以同时保留。

### 接口与输出

实现 `eraseOverlapIntervals(intervals: List[List[int]]) -> int`，返回最少删除的区间数量，而不是剩余列表或最多保留数量。输入区间不保证已经排序。

### 合法输入与约束

`1 <= len(intervals) <= 100000`，每个区间有两个端点，满足 `-50000 <= start < end <= 50000`。完全相同的重复区间会互相重叠。

### 示例

```text
输入：intervals = [[1,2],[2,3],[3,4],[1,3]]
输出：1
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/non-overlapping-intervals/description/)。

## 解题思路与参考答案

## 题意

区间数组 `intervals[i] = [start, end]`，求最少移除多少个区间，使剩下的区间两两不重叠。端点相接（如 `[1,2]` 和 `[2,3]`）不算重叠。$1\le n\le 10^5$，坐标在 $[-5\times 10^4, 5\times 10^4]$。

## 思路

我会把问题转成「最多保留多少个互不重叠区间」，最少删除就是 $n$ 减去它。最多保留是经典的活动选择，按右端点排序贪心就行。暴力枚举子集是指数级；按起点排序做 $O(n^2)$ 的 LIS 式 DP 能对，但会超时。

具体做法是按右端点升序，记当前已选区间的结束位置 `end`。下一个区间起点 $\ge$ `end` 就保留，把 `end` 更新成它的终点，否则丢掉。

按终点排，是因为在所有可选的区间里挑结束最早的，给后面留的空间最大。可以用交换论证，任何最优解的第一个区间都能换成结束最早的那个而不产生冲突，依次归纳即可。按起点排序会优先留下最早开始的区间，可能选中一个很长的区间，比如 `[1,100]` 挡住后面一串短区间。

拿 `[[1,2],[2,3],[3,4],[1,3]]` 走一遍。按终点排完是 `[1,2]`、`[2,3]`、`[1,3]`、`[3,4]`。`[1,2]` 保留，`end = 2`；`[2,3]` 起点 2 不小于 2，保留，`end = 3`；`[1,3]` 起点 1 小于 3，丢掉；`[3,4]` 保留。留下 3 个，删 1 个。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert eraseOverlapIntervals([[1, 2], [2, 3], [3, 4], [1, 3]]) == 1
assert eraseOverlapIntervals([[1, 2], [1, 2], [1, 2]]) == 2
assert eraseOverlapIntervals([[1, 2], [2, 3]]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n\log n)$，排序为主，扫描线性。额外空间 $O(1)$，不计排序。

## Edge Cases

端点相接用 $s\ge end$ 判断，`[1,2]`、`[2,3]` 都保留；写成 $s\gt end$ 会多删。

完全相同的区间只能留一个，其余全删。

坐标可以是负数，`end` 初值用 $-\infty$，用 $0$ 或 $-1$ 会出错。

## 追问

**和射气球（`lc-452-minimum-number-of-arrows-to-burst-balloons`）什么关系？**
同一套按终点贪心，区别在端点。气球是闭区间，端点相接也能被同一支箭射穿，所以换箭条件是 $s\gt end$；本题端点相接不算重叠，保留条件是 $s\ge end$。箭数等于闭区间意义下的最多不相交区间数。

**要返回具体删掉哪些区间呢？**
排序时带上原下标，贪心时没被保留的就是要删的。

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
