---
id: lc-64-minimum-path-sum
section: dp-2d
order: 2
level: A
title: LC 64 · 最小路径和
quick: "网格 DP：$dp[i][j]$ 等于当前格加上上方、左方的较小者，第一行、第一列只能沿边累加。可以原地改网格或压成一维，时间 $O(mn)$。"
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

## 题目描述

给定 m×n 的非负整数网格 grid，从左上角 `(0,0)` 出发，到达右下角 `(m-1,n-1)`。每一步只能向右或向下移动一格，路径代价为经过的所有格子数值之和，包括起点和终点。求所有合法路径中的最小代价。

### 接口与输出

实现 `minPathSum(grid: List[List[int]]) -> int`，返回最小路径和，不必返回路径坐标。

### 合法输入与约束

`1 <= m,n <= 200`，`0 <= grid[i][j] <= 200`。网格矩形且非空；不能向上、向左或斜向移动。

### 示例

```text
输入：grid = [[1,3,1],[1,5,1],[4,2,1]]
输出：7
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/minimum-path-sum/description/)。

## 解题思路与参考答案

## 题意

$m\times n$ 网格，从左上走到右下，只能向右或向下，求路径上数字和的最小值。

## 思路

我会用网格 DP。只能向右或向下，走到 $(i,j)$ 的上一步只能来自上方或左方，所以 $dp[i][j]$ 就是当前格加上两者中较小的那个。第一行没有上方，第一列没有左方，各自沿边累加。

拿 `[[1,3,1],[1,5,1],[4,2,1]]` 来说，第一行累加成 `1, 4, 5`；第二行是 `2, 7, 6`，中间那格是 `5 + min(4, 2) = 7`；第三行是 `6, 8, 7`，答案 $7$。

可以原地写回 `grid`，也可以一维滚动：`dp[j]` 在更新前是上一行的 $j$（上方），`dp[j-1]` 是本行左侧。白板上我先写二维，再压缩。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert minPathSum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]) == 7
assert minPathSum([[1, 2, 3], [4, 5, 6]]) == 12
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$；原地修改额外空间 $O(1)$，另开 DP 是 $O(mn)$，一维滚动是 $O(n)$。

## 边界

$1\times n$ 或 $m\times 1$ 没有分叉，答案就是这一条的累加。值为 $0$ 的格子照常走 DP，零代价不等于障碍，不能跳过。单格时循环里 `i==0 and j==0` 直接跳过，返回该格本身。

## 追问

**不能改原数组怎么办？**
那就开一行 `dp[j]`，它在更新前是上一行的「上」，`dp[j-1]` 是本行的「左」。第一行没有上方，用 $+\infty$ 挡掉，额外空间 $O(n)$。

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

**改成求路径条数（LC 62 / 63）呢？**
把 $\min$ 换成加法：无障碍时 `dp[j] += dp[j-1]`，初值 `dp[0]=1`；有障碍就把该格置 $0$。无障碍时还可以直接算 $C(m+n-2,m-1)$。独立卡见 `lc-63-unique-paths-ii`。

```python
def uniquePaths(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[-1]
```

**要输出一条最小路径呢？**
保留二维 `dp`（或者原地改过的网格），从右下往回走：比较上方和左方，走较小的那个（相等任选），一直走到左上。路径要用原网格的值的话，回溯前先拷一份，或另开 `dp` 不改原数组。时间 $O(mn)$，回溯 $O(m+n)$。

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
