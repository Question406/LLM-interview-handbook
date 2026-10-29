---
id: lc-57-insert-interval
section: intervals
order: 3
level: A
title: LC 57 · 插入区间
quick: 原区间已经有序且不重叠，一遍扫描分三段：完全在新区间左边的原样抄，和它重叠的并成一段，完全在右边的再抄上。时间 $O(n)$。
tags:
  - Intervals
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 57. 插入区间
    url: 'https://leetcode.cn/problems/insert-interval/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定按起点递增排列、彼此不重叠的闭区间列表 intervals，以及一个待插入闭区间 newInterval。把新区间纳入现有区间覆盖范围，必要时合并发生重叠的部分，返回仍然按起点有序且互不重叠的区间列表。

### 接口与输出

实现 `insert(intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]`。返回完整结果，不要求在原列表上原地完成。闭区间端点相接也有交点，因此需要合并。

### 合法输入与约束

`0 <= len(intervals) <= 10000`；每个区间均为 `[start,end]`，满足 `0 <= start <= end <= 100000`，newInterval 也满足同一约束。原列表可以为空。

### 示例

```text
输入：intervals = [[1,3],[6,9]], newInterval = [2,5]
输出：[[1,5],[6,9]]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/insert-interval/description/)。

## 解题思路与参考答案

## 题意

`intervals` 已按起点排序且互不重叠。插入 `newInterval`，必要时和重叠的段合并，返回的仍是有序不重叠的列表。

## 思路

原表已经有序，我就不整表排序了（那是 LC 56 的做法），一次扫描分三段处理。先是 `intervals[i].end < new.start` 的区间，它们完全在左边，直接放进答案。接着是 `intervals[i].start <= new.end` 的区间，它们和新区间有重叠，把 `new` 的左右端扩到能盖住这些段。剩下的都完全在右边，原样追加。中间那段扩完只插入一次合并后的 `new`。

拿 `[[1,2],[3,5],[6,7],[8,10],[12,16]]` 插入 `[4,8]` 走一遍：`[1,2]` 在左边，直接抄；`[3,5]`、`[6,7]`、`[8,10]` 都和新区间重叠，新区间被扩成 `[3,10]`；`[12,16]` 在右边，抄上。结果是 `[[1,2],[3,10],[12,16]]`。

新区间也可能落在最前、最后，或者把中间若干段全吃掉，三段的写法都能覆盖。

## 参考代码

```python
from typing import List


def insert(intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
    res = []
    i, n = 0, len(intervals)
    ns, ne = newInterval
    while i < n and intervals[i][1] < ns:
        res.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= ne:
        ns = min(ns, intervals[i][0])
        ne = max(ne, intervals[i][1])
        i += 1
    res.append([ns, ne])
    while i < n:
        res.append(intervals[i])
        i += 1
    return res


if __name__ == "__main__":
    assert insert([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
    assert insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]) == [
        [1, 2],
        [3, 10],
        [12, 16],
    ]
    assert insert([], [5, 7]) == [[5, 7]]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert insert([[1, 3], [6, 9]], [2, 5]) == [[1, 5], [6, 9]]
assert insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]) == [
    [1, 2],
    [3, 10],
    [12, 16],
]
assert insert([], [5, 7]) == [[5, 7]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$（答案）。每个原区间只访问一次。

## Edge Cases

原列表为空时，答案就是 `[newInterval]`。新区间在最左或最右时，第一段或第三段吃掉全部原区间。和所有段都重叠时，中间循环把 `ns/ne` 扩成并集，只插一次。和任何段都不重叠时，它夹在某两段中间，中间循环零次。新区间被某段完全包含时，`ns/ne` 扩回那一段，答案长度不变。

## 追问

**原区间没排序呢？**
先把 `newInterval` 放进列表，再按合并区间来做：按起点排序，能重叠就扩 `end`，否则新开一段。时间 $O(n\log n)$，不用自己写三段扫描。这就是 LC 56，单独一张卡 `lc-56-merge-intervals`。只插一次、整表又无序时，排序就够了；如果已经有序，就别退回这条 $O(n\log n)$ 的路。

```python
def insertUnsorted(intervals, newInterval):
    intervals = intervals + [newInterval]
    intervals.sort()
    res = [intervals[0][:]]
    for s, e in intervals[1:]:
        if s <= res[-1][1]:
            res[-1][1] = max(res[-1][1], e)
        else:
            res.append([s, e])
    return res
```

**要在线插入很多段呢？**
维护当前互不重叠的有序区间。每次插入用二分找到可能重叠的左邻（左邻 $end \ge new.start$ 就退一格），再向右吞掉所有 $start \le new.end$ 的段，把并集写回去。用 `list` + `bisect` 单次要移动元素，是 $O(n)$；真正做到 $O(\log n)$ 要用平衡树。重叠判定和这题一样，闭区间端点相接也要合并。别每次插入都整表 `sort`。

```python
import bisect


def insertOnline(starts, ends, s, e):
    i = bisect.bisect_left(starts, s)
    if i and ends[i - 1] >= s:
        i -= 1
        s = starts[i]
    j = i
    while j < len(starts) and starts[j] <= e:
        e = max(e, ends[j])
        s = min(s, starts[j])
        j += 1
    starts[i:j], ends[i:j] = [s], [e]
```
