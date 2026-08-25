---
id: lc-64-minimum-path-sum
section: dp-2d
order: 2
level: A
title: LC 64 · 最小路径和
quick: >-
  只能向右或向下。$dp[i][j]$ 等于当前格加上上方、左方的较小者。第一行 / 列只能沿边累加。可压成一维或原地改网格。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 64. 最小路径和
    url: https://leetcode.cn/problems/minimum-path-sum/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$m\times n$ 网格，从左上走到右下，只能向右或向下，求路径数字和的最小值。

## 思路

$dp[i][j]$ 表示走到 $(i,j)$ 的最小和。转移是当前格加上上方、左方的较小者。第一行没有上方，第一列没有左方，各自沿边累加。

可以原地写回 `grid`，或一维滚动：`dp[j]` 表示上一行的 $j$（上方），`dp[j-1]` 是本行左侧。白板我先写二维转移，再压缩。

## 参考代码

```python
from typing import List


def minPathSum(grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            up = grid[i - 1][j] if i else 10**18
            left = grid[i][j - 1] if j else 10**18
            grid[i][j] += min(up, left)
    return grid[-1][-1]


if __name__ == "__main__":
    assert minPathSum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
    assert minPathSum([[1, 2, 3], [4, 5, 6]]) == 12
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间原地 $O(1)$；另开 DP 则 $O(mn)$ 或一维 $O(n)$。

## 边界

- $1\times n$ 或 $m\times 1$：没有分叉，答案就是这一条的累加。
- 含 $0$：零代价格仍走 DP，不能当障碍跳过。
- 单格：循环里 `i==0 and j==0` 直接跳过，返回该格本身。

## 追问

- **不能改原数组？** 开一行 `dp[j]`：它在更新前是上一行的上，`dp[j-1]` 是本行的左。第一行没有上方，用 $+\infty$ 挡掉。额外空间 $O(n)$。

```python
def minPathSum_roll(grid):
    inf, n = 10**18, len(grid[0])
    dp = [inf] * n
    for i, row in enumerate(grid):
        dp[0] = row[0] + (0 if i == 0 else dp[0])
        for j in range(1, n):
            up = dp[j] if i else inf
            dp[j] = row[j] + min(up, dp[j - 1])
    return dp[-1]
```

- **改成路径条数（LC 62 / 63）？** 把 $\min$ 换成加法：无障碍时 `dp[j] += dp[j-1]`，初值 `dp[0]=1`；有障碍则该格置 $0$。无障碍还可直接 $C(m+n-2,m-1)$。独立卡见 `lc-63-unique-paths-ii`。

```python
def uniquePaths(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[-1]
```

- **输出一条最小路径？** 保留二维 `dp`（或原地改过的网格）。从右下往回走：比较上方与左方，选较小者（相等任选），直到左上。路径要原网格值的话，回溯前先拷一份，或另开 `dp` 不改原数组。时间 $O(mn)$，回溯 $O(m+n)$。

```python
def minPath_recover(grid):
    m, n = len(grid), len(grid[0])
    dp = [row[:] for row in grid]
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            up = dp[i - 1][j] if i else 10**18
            left = dp[i][j - 1] if j else 10**18
            dp[i][j] += min(up, left)
    path, i, j = [], m - 1, n - 1
    while True:
        path.append(grid[i][j])
        if i == j == 0:
            break
        up = dp[i - 1][j] if i else 10**18
        left = dp[i][j - 1] if j else 10**18
        if up <= left:
            i -= 1
        else:
            j -= 1
    path.reverse()
    return dp[-1][-1], path
```
