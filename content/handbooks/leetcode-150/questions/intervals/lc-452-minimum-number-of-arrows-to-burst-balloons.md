---
id: lc-452-minimum-number-of-arrows-to-burst-balloons
section: intervals
order: 4
level: A
title: LC 452 · 用最少数量的箭引爆气球
quick: >-
  按气球右端点排序，一支箭钉在当前这组的终点；下一个气球起点仍 $\le$ 这个终点就同一支箭，否则再射一支钉在它的终点。时间 $O(n\log n)$。
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

## 题目描述

给定气球列表 `points`，每个气球用闭区间 `[start,end]` 表示其水平方向的范围。选择一个水平位置 x 向上射箭，会同时引爆所有满足 `start <= x <= end` 的气球。不同气球可以相互重叠，箭的数量没有预设上限。求引爆全部气球至少需要多少支箭。

### 输入与输出

实现 `findMinArrowShots(points) -> int`，返回最少箭数，不要求返回射箭位置。区间包含两个端点，所以一支射在公共端点上的箭可以同时命中相接的两个气球。

### 约束

- `1 <= len(points) <= 10^5`，每个区间恰好有两个端点。
- `-2^31 <= start < end <= 2^31 - 1`。

### 示例

```text
输入：points = [[10,16],[2,8],[1,6],[7,12]]
输出：2
```

[LeetCode 原题](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/description/)

## 解题思路与参考答案

## 题意

每个气球是一个闭区间 `[start, end]`。一支箭射在整数 $x$ 上，能射爆所有覆盖 $x$ 的气球。求射爆全部气球最少要几支箭。

## 思路

我会按终点升序排序再贪心。最早结束的那个气球决定了这支箭最晚必须落在哪，把箭钉在它的终点，能给后面的气球留出最大的重叠，所以排序键用终点。

第一支箭射在第一个气球的终点，能顺带打掉所有起点不超过这个终点的气球。遇到起点比箭的位置还大的气球，这支箭够不着，就再射一支，钉在这个气球的终点。

拿 `[[10,16],[2,8],[1,6],[7,12]]` 来说，按终点排好是 `[1,6]`、`[2,8]`、`[7,12]`、`[10,16]`。第一支箭钉在 6，`[2,8]` 起点 2 不超过 6，一起射爆；`[7,12]` 起点 7 大于 6，再射一支钉在 12，`[10,16]` 起点 10 不超过 12，也一起射爆。一共 2 支。

气球是闭区间，端点相等也能用同一支箭。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert findMinArrowShots([[10, 16], [2, 8], [1, 6], [7, 12]]) == 2
assert findMinArrowShots([[1, 2], [3, 4], [5, 6], [7, 8]]) == 4
assert findMinArrowShots([[1, 2], [2, 3], [3, 4], [4, 5]]) == 2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n\log n)$，额外空间 $O(1)$（不计排序）。贪心扫描本身是线性的。

## 边界

只有一个气球时排完直接返回 $1$。全部重叠时一直满足 $start\le end$，只射一支。只在端点相接时，闭区间 `[1,2]` 和 `[2,3]` 能共用一支箭，所以代码里 $start \gt end$ 才换箭。负坐标照样比较和排序，不用平移。零宽度气球（`start == end`）仍占一个点，钉在这个点上的箭能射中它。

## 追问

**改成开区间呢？**
端点相接就不能再共用一支箭了。把判断从 $start \gt end$ 改成 $start \ge end$，也就是当前气球的起点已经不小于箭的位置，就覆盖不到。其余不变，仍然按右端点升序，箭钉在当前组的终点，时间 $O(n\log n)$。排序键别跟着改，还是按终点排。先确认题面是闭区间还是开区间，这题容易栽在这个符号上。

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

**和「最多不重叠区间」（活动选择）是什么关系？**
是同一套按终点贪心：右端点升序以后，能选就选。闭区间下这题的「最少箭数」恰好等于「最多互不重叠的气球数」。每支箭钉在一组重叠气球的最右端，下一支必须开新组，组数就是最大不相交子集的大小。活动选择要的是保留数 `keep`；如果问删掉多少个才能不重叠（LC 435），答案是 $n-\textit{keep}$。判定符号要分清：活动选择里端点相接通常允许保留（$s \ge last\_end$ 可保留），而这题闭区间相接算同一支箭（$s \gt end$ 才换箭）。也别和合并区间搞混，合并求的是并集，这题求的是点覆盖。合并的卡见 `lc-56-merge-intervals`。

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
