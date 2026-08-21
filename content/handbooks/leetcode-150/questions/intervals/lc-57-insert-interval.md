---
id: lc-57-insert-interval
section: intervals
order: 3
level: A
title: LC 57 · 插入区间
quick: >-
  原区间已有序不重叠。分三段：完全在新区间左边的原样抄；与之重叠的并成一段；完全在右边的再抄上。时间
  $O(n)$。
tags:
  - Intervals
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 57. 插入区间
    url: https://leetcode.cn/problems/insert-interval/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`intervals` 已按起点排序且互不重叠。插入 `newInterval`，必要时与重叠段合并，仍返回有序不重叠列表。

## 思路

不要整表排序（那是 LC 56）。一次扫描分三段：

1. `intervals[i].end < new.start`：完全在左，直接放入答案。
2. `intervals[i].start <= new.end`：有重叠，把 `new` 的左右端扩到覆盖这些段。
3. 其余完全在右，追加。

中间那段扩完只插入一次合并后的 `new`。新区间也可能落在最前、最后，或把中间若干段全吃掉。

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

## 复杂度

时间 $O(n)$，额外空间 $O(n)$（答案）。每个原区间访问一次。

## 边界

- 原列表为空：答案就是 `[newInterval]`。
- 新区间在最左 / 最右：第一段或第三段吃掉全部原区间。
- 与所有段重叠：中间循环把 `ns/ne` 扩成并集，只插一次。
- 与任何段都不重叠：夹在某两段中间，中间循环零次。
- 新区间被某段完全包含：`ns/ne` 扩回该段，答案长度不变。

## 追问

- **原区间未排序？** 先把 `newInterval` 丢进列表，再走合并区间：按起点排序，能重叠就扩 `end`，否则新开一段。时间 $O(n\log n)$，不必自己写三段扫。这就是 LC 56。独立卡见 `lc-56-merge-intervals`。若只有一次插入却整表无序，排序是值得的；若已有序，不要退回这条 $O(n\log n)$ 路。

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

- **在线插入很多段？** 维护当前互不重叠的有序区间。每次插入用二分找到可能重叠的左邻（左邻 $end \ge new.start$ 则退一格），向右吞掉所有 $start \le new.end$ 的段，再把并集写回。`list` + `bisect` 单次移动 $O(n)$；真正 $O(\log n)$ 要用平衡树。重叠判定与本题相同：闭区间端点相接也要并。不要每次插入都整表 `sort`。

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
