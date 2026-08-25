---
id: lc-63-unique-paths-ii
section: dp-2d
order: 3
level: A
title: LC 63 · 不同路径 II
quick: >-
  有障碍。障碍格 $dp=0$。其余 $dp[i][j]$ 为上方加左方。起点若是障碍则直接 $0$。一维滚动时障碍要把
  `dp[j]` 置零。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 63. 不同路径 II
    url: https://leetcode.cn/problems/unique-paths-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

网格 `obstacleGrid`，`1` 是障碍，`0` 可走。从左上到右下，只能右或下，求路径条数。

## 思路

LC 62 加障碍：障碍格方案数为 $0$，不能往外贡献。其余格仍是上方加左方。起点是障碍则答案 $0$。

第一行 / 列一旦出现障碍，后面整段都是 $0$。一维 `dp[j]`：本行障碍则置 $0$，否则加上 `dp[j-1]`（左）。白板我先画清「障碍切断前缀」。

## 参考代码

```python
from typing import List


def uniquePathsWithObstacles(obstacleGrid: List[List[int]]) -> int:
    m, n = len(obstacleGrid), len(obstacleGrid[0])
    dp = [0] * n
    dp[0] = 0 if obstacleGrid[0][0] else 1
    for i in range(m):
        for j in range(n):
            if obstacleGrid[i][j]:
                dp[j] = 0
            elif j > 0:
                dp[j] += dp[j - 1]
    return dp[-1]


if __name__ == "__main__":
    assert uniquePathsWithObstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2
    assert uniquePathsWithObstacles([[0, 1], [0, 0]]) == 1
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间 $O(n)$。

## 边界

- 起点是障碍：`dp[0]=0`，后面全是 $0$。
- 终点是障碍：该格被置 $0$，答案 $0$。
- 第一行 / 列中途出现障碍：障碍及之后整段为 $0$，因为只能沿边走。
- 全无障碍：退化为 LC 62，方案数是组合数 $C(m+n-2, m-1)$。

## 追问

- **没有障碍（LC 62）？** 仍可滚动：`dp[j] += dp[j-1]`，初值全 $1$。也可直接算组合数，连乘时边乘边整除，避免溢出。时间 $O(\min(m,n))$。

```python
def uniquePaths(m, n):
    a, b = m + n - 2, min(m, n) - 1
    ans = 1
    for i in range(1, b + 1):
        ans = ans * (a - b + i) // i
    return ans
```

- **最小路径和带障碍？** 可走格仍取上、左较小者再加代价；障碍格不能往外贡献。下面用负数标记障碍，滚动时写成 $+\infty$。终点仍是 $\infty$ 则无路，返回 $-1$。时间 $O(mn)$。

```python
def minPathObstacles(grid):
    inf = 10**18
    n, dp = len(grid[0]), [inf] * len(grid[0])
    for i, row in enumerate(grid):
        for j, x in enumerate(row):
            if x < 0:
                dp[j] = inf
                continue
            if i == 0 and j == 0:
                dp[0] = x
            else:
                dp[j] = x + min(dp[j], dp[j - 1] if j else inf)
    return -1 if dp[-1] >= inf else dp[-1]
```

- **路径数要取模？** 无障碍时 $C(m+n-2,m-1)$ 很快超过 32 位。按题意每次加法对 $10^9+7$ 取模；障碍置零后再加。Python 无限整数可以最后再模，白板仍建议滚动时就模。

```python
def uniquePathsWithObstacles_mod(grid, mod=10**9 + 7):
    n, dp = len(grid[0]), [0] * len(grid[0])
    dp[0] = 0 if grid[0][0] else 1
    for i, row in enumerate(grid):
        for j, x in enumerate(row):
            if x:
                dp[j] = 0
            elif j:
                dp[j] = (dp[j] + dp[j - 1]) % mod
    return dp[-1]
```
