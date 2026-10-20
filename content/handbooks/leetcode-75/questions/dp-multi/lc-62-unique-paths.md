---
id: lc-62-unique-paths
section: dp-multi
order: 1
level: S
title: LC 62 · 不同路径
quick: >-
  每个格子只能从上方或左侧到达，因此 $dp[i][j]=dp[i-1][j]+dp[i][j-1]$，第一行第一列都是 $1$。只保留一行状态时，用 `dp[j] += dp[j-1]` 更新。时间
  $O(mn)$，额外空间 $O(n)$；也可直接算组合数 $\binom{m+n-2}{m-1}$。
tags:
  - DP
  - Math
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 62. Unique Paths
    url: https://leetcode.com/problems/unique-paths/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

$m\times n$ 网格，机器人从左上角出发，每步只能向右或向下，走到右下角。求不同路径数。$1\le m, n\le 100$，答案不超过 $2\times 10^9$。

## 思路

$dp[i][j]$ 是走到格子 $(i,j)$ 的路径数。最后一步要么从上方下来，要么从左边过来，两类不重不漏：

$dp[i][j]=dp[i-1][j]+dp[i][j-1]$，第一行、第一列只有一条路，都是 $1$。

每行只依赖上一行和本行左边，所以一维数组从左往右 `dp[j] += dp[j-1]` 就够：加之前的 `dp[j]` 是上一行，`dp[j-1]` 已经是本行。换个角度看，总共要走 $m-1$ 次下、$n-1$ 次右，路径数就是在 $m+n-2$ 步里挑哪几步向下，$\binom{m+n-2}{m-1}$。DFS 暴力枚举路径是指数级，不可取。

## 参考代码

```python
from math import comb


def uniquePaths(m: int, n: int) -> int:
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[-1]


if __name__ == "__main__":
    assert uniquePaths(3, 7) == 28
    assert uniquePaths(3, 2) == 3
    assert uniquePaths(1, 1) == 1
    assert uniquePaths(1, 5) == 1
    assert uniquePaths(7, 3) == 28
    for m in range(1, 15):
        for n in range(1, 15):
            assert uniquePaths(m, n) == comb(m + n - 2, m - 1)
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间 $O(n)$。组合数写法时间 $O(\min(m,n))$，额外空间 $O(1)$。

## 边界

- $m=1$ 或 $n=1$：只有一条直线路径，答案 $1$。
- $m, n$ 互换答案不变，可以让一维数组取较短的一边。
- 组合数手算时要边乘边除（每步乘完再整除），避免中间结果溢出或出现小数。

## 追问

- **网格里有障碍（LC 63）？** 障碍格 $dp=0$，其余转移不变。第一行第一列不能再直接填 $1$：遇到障碍后面全是 $0$。一维写法里把起点设 $1$，遇障碍把 `dp[j]` 清零即可统一处理。

```python
def uniquePathsWithObstacles(grid):
    n = len(grid[0])
    dp = [0] * n
    dp[0] = 1
    for row in grid:
        for j in range(n):
            if row[j] == 1:
                dp[j] = 0
            elif j > 0:
                dp[j] += dp[j - 1]
    return dp[-1]
```

- **不用库函数怎么算组合数？** 取 $k=\min(m,n)-1$，`res = res * (m + n - 2 - k + i) // i` 从 $i=1$ 乘到 $k$。每一步的中间值都是某个组合数，所以整除不会丢精度。

```python
def uniquePathsComb(m, n):
    k = min(m, n) - 1
    total = m + n - 2
    res = 1
    for i in range(1, k + 1):
        res = res * (total - k + i) // i
    return res
```
