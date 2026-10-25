---
id: ali-algo-path-rect
section: alibaba-oa
order: 40
level: A
title: 阿里手撕：最小路径和、最大矩形的 DP 怎么设？
quick: >-
  最小路径和（64）只能向右或向下，`dp=grid+min(上,左)`，第一行和第一列只能单向累加。最大矩形（85）逐行累积各列连续为 1 的高度，把每一行变成直方图，再用 84 的单调栈求最大面积，整题 $O(mn)$。
tags:
  - Alibaba
  - DP
  - 单调栈
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 最小路径和
    url: https://leetcode.cn/problems/minimum-path-sum/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 题目描述

本卡包含两个网格任务和一个独立的柱状图接口：求只向右或向下移动的最小路径和；求二进制矩阵中只含 1 的最大轴对齐矩形面积；求柱状图最大矩形面积。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

`min_path_sum(grid)` 接受非空、每行等长的整数网格；从左上角到右下角移动。`maximal_rectangle(matrix)` 接受由字符 `"0"`、`"1"` 组成的矩阵，可为空。`largest_rectangle_area(heights)` 接受非负整数高度列表，每根柱宽为 1。

### 输出与约束

路径和包含起点、终点及沿途格子。两个矩形接口返回面积，不能跨越 0 或超过柱高；空矩阵或空柱状图的面积为 0。不要求返回路径或矩形坐标。

### 示例

```text
min_path_sum([[1,3,1],[1,5,1],[4,2,1]]) -> 7
maximal_rectangle([["1","1"],["1","0"]]) -> 2
largest_rectangle_area([2,1,2]) -> 3
```

## 解题思路与参考答案

64 是网格里只能往右、往下走的最短路 DP；85 是把矩阵逐行压成直方图，再套 84 的柱状图最大矩形。两题都是 $O(mn)$，别去枚举每个左上角和右下角。这两道（LeetCode 64 / 85）在阿里算中频，但爱考实现。

最小路径和的转移是 `dp[i][j]=\mathrm{grid}[i][j]+\min(\mathrm{dp}[i-1][j],\,\mathrm{dp}[i][j-1])`：走到 $(i,j)$ 只能从上面或左边来，取便宜的那个。第一行和第一列没有「上」或「左」，只能沿唯一的方向累加。空间可以滚动成 $O(n)$，也可以直接原地改 `grid`。带障碍物的版本（63）把障碍格的路径数设成 $0$，起点就是障碍的话答案是 $0$。

最大矩形逐行维护 `height[j]`，也就是到当前这一行为止，第 $j$ 列连续 $1$ 的高度，遇到 $0$ 就清零。不清零的话直方图会「悬空」，算出来的矩形中间其实夹着 0。每一行的高度数组都跑一遍 84：单调递增栈存下标，弹出时宽度是 $i-\mathrm{stack.top}()-1$。每层单调栈是 $O(n)$，所以整题 $O(mn)$ 时间、$O(n)$ 空间。

```python
from typing import List


def min_path_sum(grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    dp = [row[:] for row in grid]
    for i in range(1, m):
        dp[i][0] += dp[i - 1][0]
    for j in range(1, n):
        dp[0][j] += dp[0][j - 1]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] += min(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def largest_rectangle_area(heights: List[int]) -> int:
    stack = [-1]
    ans = 0
    hs = heights + [0]
    for i, h in enumerate(hs):
        while stack[-1] != -1 and hs[stack[-1]] > h:
            height = hs[stack.pop()]
            width = i - stack[-1] - 1
            if height * width > ans:
                ans = height * width
        stack.append(i)
    return ans


def maximal_rectangle(matrix: List[List[str]]) -> int:
    if not matrix:
        return 0
    n = len(matrix[0])
    heights = [0] * n
    ans = 0
    for row in matrix:
        for j, v in enumerate(row):
            heights[j] = heights[j] + 1 if v == "1" else 0
        area = largest_rectangle_area(heights)
        if area > ans:
            ans = area
    return ans


if __name__ == "__main__":
    assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    assert min_path_sum([[1, 2, 3], [4, 5, 6]]) == 12
    grid = [
        ["1", "0", "1", "0", "0"],
        ["1", "0", "1", "1", "1"],
        ["1", "1", "1", "1", "1"],
        ["1", "0", "0", "1", "0"],
    ]
    assert maximal_rectangle(grid) == 6
    assert maximal_rectangle([["0"]]) == 0
    print("ok")
```

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**要测哪些边界？**
64 测 $1\times 1$、单行、单列；85 测全 $0$、全 $1$、单列。

**格子里有负权，还是只能往右下走，要换 Dijkstra 吗？**
没必要，还是这套 DP。只有允许四个方向走的时候，才需要谈最短路算法。
