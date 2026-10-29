---
id: lc-452-minimum-number-of-arrows-to-burst-balloons
section: intervals
order: 2
level: A
title: LC 452 · 用最少数量的箭引爆气球
quick: >-
  按气球右端点排序贪心，每支箭钉在当前组第一个气球的终点，这是能射到它的最右位置。下一个起点仍 $\le$ 该终点就用同一支箭，否则再射一支。时间
  $O(n\log n)$，额外空间 $O(1)$（不计排序）。
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
  - title: 452. Minimum Number of Arrows to Burst Balloons
    url: 'https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

有若干气球，每个气球在 x 轴方向占据一个闭区间 [start,end]。在任意实数横坐标 x 处向上射一支箭，就能射爆所有满足 start<=x<=end 的气球；箭穿过一个气球后还能继续射爆同一坐标上的其他气球。求射爆全部气球所需的最少箭数。

### 输入与输出

实现 `findMinArrowShots(points) -> int`。points[i] 含该气球的左右端点，只返回最少箭数，不用返回射箭位置。区间端点也属于气球，因此只在端点相接的两个区间也可能被同一支箭击中。

### 约束与约定

- `1 <= len(points) <= 100000`。
- 每个区间恰好有两个 32 位有符号整数端点，且 start 严格小于 end。

### 示例

```text
输入：points = [[10,16],[2,8],[1,6],[7,12]]
输出：2
```

示例可以在 x=6 和 x=11 各射一箭，分别覆盖两组气球，总共两箭。

[官方原题与完整题面](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/description/)。

## 解题思路与参考答案

## 题意

每个气球是 x 轴上的闭区间 `[start, end]`。在 $x$ 处竖直射一支箭，能射爆所有满足 $start\le x\le end$ 的气球，箭穿过后继续飞。求射爆全部气球的最少箭数。$1\le n\le 10^5$，坐标在 32 位有符号整数范围内。

## 思路

我会按终点升序贪心，每支箭都射在当前这组第一个气球的终点。结束最早的气球决定了这支箭最晚必须落在哪，把箭放在这个最晚位置，能顺带打掉所有起点不超过该终点的气球，给后面留最大重叠。遇到起点大于当前箭位的气球，这支箭够不着，就再射一支，钉在它的终点。端点相等也能同箭，因为是闭区间，所以换箭条件是 $start\gt end$。

拿 `[[10,16],[2,8],[1,6],[7,12]]` 走一遍。按终点排完是 `[1,6]`、`[2,8]`、`[7,12]`、`[10,16]`。第一支箭钉在 6，`[2,8]` 起点 2 不超过 6，一起射爆；`[7,12]` 起点 7 大于 6，射第二支，钉在 12；`[10,16]` 起点 10 不超过 12，同一支箭。一共 2 支。

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
    assert findMinArrowShots([[-(2**31), 2**31 - 1], [0, 0]]) == 1
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

时间 $O(n\log n)$，额外空间 $O(1)$（不计排序）。贪心扫描线性。

## Edge Cases

只有一个气球时直接返回 $1$。

只在端点相接的闭区间，比如 `[1,2]` 与 `[2,3]`，可以同箭，代码用 $start\gt end$ 才换箭。

坐标会到 32 位极端值，Java / C++ 里按 `a[1] - b[1]` 排序会溢出，要用比较函数；Python 没这个问题。

零宽度气球（`start == end`）仍占一个点，钉在该点的箭能射中它。

## 追问

**改成开区间呢？**
端点相接就不再共用一支箭。把判断从 $start\gt end$ 改成 $start\ge end$，其余不变。先跟面试官确认题面是闭区间还是开区间，这块容易栽在符号上。

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

**和无重叠区间（`lc-435-non-overlapping-intervals`）什么关系？**
同一套按终点贪心。每支箭对应一组重叠气球，组数就是闭区间意义下的最多互不相交气球数；LC 435 求的是 $n$ 减去最多保留数，而且端点相接不算重叠，保留条件是 $s\ge end$。另外别和合并区间搞混，合并要的是并集，这题要的是点覆盖。
