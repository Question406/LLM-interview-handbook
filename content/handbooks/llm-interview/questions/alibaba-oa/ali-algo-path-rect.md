---
id: ali-algo-path-rect
section: alibaba-oa
order: 40
level: A
title: 阿里手撕：最小路径和、最大矩形的 DP 怎么设？
quick: >-
  64 只能右/下，`dp=grid+min(上,左)`。85 我对每一层当直方图，用 84 的单调栈求最大矩形。
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

## 真题 / 考点说明

- 对应：LeetCode 64 / 85（中频但爱考实现）

64 是网格只能向右/向下的最短路 DP。85 是「逐行压成直方图 + 柱状图最大矩形」。不要对每个左上右下枚举。障碍物版本（63）把障碍设为 $0$ 条路径。

## 思路

路径和：`dp[i][j]=\mathrm{grid}[i][j]+\min(\mathrm{dp}[i-1][j],\,\mathrm{dp}[i][j-1])`。第一行/列只能累加一条边，没有「上」或「左」时只走唯一方向。可原地改 `grid` 省空间。

最大矩形：逐行维护 `height[j]`：当前列连续 $1$ 的高度，遇 $0$ 清零。对每一层的高度数组跑 84：单调递增栈存下标，弹出时宽为 $i-\mathrm{stack.top}()-1$。整题 $O(mn)$。

## 参考代码

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

## 复杂度

两题都是 $O(mn)$ 时间。64 可 $O(n)$ 滚动或原地。85 每层单调栈 $O(n)$，总空间 $O(n)$。不要枚举所有子矩形。

## 边界与追问

1. 64：$1\times 1$、单行/单列。63 有障碍：障碍格路径数置 $0$，起点是障碍则答案 $0$。
2. 85：全 $0$、全 $1$、单列。高度遇 $0$ 必须清零，否则直方图会「悬空」。
3. 追问「只能右下且有负权」：仍是这套 DP，Dijkstra 没必要；若可四向再谈最短路。
