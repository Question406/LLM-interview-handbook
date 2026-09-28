---
id: lc-221-maximal-square
section: dp-2d
order: 9
level: A
title: LC 221 · 最大正方形
quick: >-
  $dp[i][j]$：以 $(i,j)$ 为右下角的最大正方形边长。格子为
  $1$ 时 $dp[i][j]=\min(\text{上},\text{左},\text{左上})+1$，否则 $0$。答案是最大边长的平方。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 221. 最大正方形
    url: https://leetcode.cn/problems/maximal-square/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`0`/`1` 矩阵，找只含 `1` 的最大正方形，返回它的面积。

## 思路

$dp[i][j]$ 定义为「以该格为右下角」能形成的最大边长。当前是 `0` 则 $0$。当前是 `1` 时，边长受上、左、左上三个方向短板限制：三者取 $\min$ 再加一。三个方向都至少有边长 $k-1$，才能在这里收成 $k$。

下标可以整体加一圈空边，省掉边界特判。最后返回 $\textit{side}^2$，不是边长。

## 参考代码

```python
from typing import List


def maximalSquare(matrix: List[List[str]]) -> int:
    m, n = len(matrix), len(matrix[0])
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    side = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if matrix[i - 1][j - 1] == "1":
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
                side = max(side, dp[i][j])
    return side * side


if __name__ == "__main__":
    assert (
        maximalSquare(
            [
                ["1", "0", "1", "0", "0"],
                ["1", "0", "1", "1", "1"],
                ["1", "1", "1", "1", "1"],
                ["1", "0", "0", "1", "0"],
            ]
        )
        == 4
    )
    assert maximalSquare([["0", "1"], ["1", "0"]]) == 1
    assert maximalSquare([["0"]]) == 0
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$，可滚成一维 $O(n)$。

## 边界

- 全 $0$：`side` 保持 $0$，面积 $0$。
- 单格 `"1"`：三个邻居都是哨兵 $0$，$\min+1=1$，面积 $1$。
- 最大正方形贴边：多开一圈空边后第一行 / 列按普通格子转移，不必特判。

## 追问

- **最大矩形不是正方形（LC 85）？** 正方形靠「上 / 左 / 左上」三条边长的短板，矩形宽高解耦，这个 $\min$ 用不了。逐行把当前格上方连续 `1` 收成直方图高度，再对每一层直方图用单调栈求最大矩形。时间 $O(mn)$。

```python
def maximalRectangle(matrix):
    if not matrix:
        return 0
    n, heights, ans = len(matrix[0]), [0] * len(matrix[0]), 0
    for row in matrix:
        for j, x in enumerate(row):
            heights[j] = heights[j] + 1 if x == "1" else 0
        st, h = [-1], heights + [0]
        for i, x in enumerate(h):
            while st[-1] != -1 and h[st[-1]] > x:
                height = h[st.pop()]
                ans = max(ans, height * (i - st[-1] - 1))
            st.append(i)
    return ans
```

- **压成一维，对角为什么会脏？** 转移要用上、左、左上。滚动后 `dp[j]` 写之前是上一行的上；`dp[j-1]` 已经是本行的左。左上本应是上一行的 `dp[j-1]`，但它刚被本行覆盖。所以写 `dp[j]` 前先把旧值存进 `prev`，下一列的对角就用这个旧值。漏存会把本行左边当成左上，边长虚高。

```python
def maximalSquare_1d(matrix):
    n, side = len(matrix[0]), 0
    dp = [0] * (n + 1)
    for i in range(1, len(matrix) + 1):
        prev = 0
        for j in range(1, n + 1):
            tmp = dp[j]
            if matrix[i - 1][j - 1] == "1":
                dp[j] = min(dp[j], dp[j - 1], prev) + 1
                side = max(side, dp[j])
            else:
                dp[j] = 0
            prev = tmp
    return side * side
```
