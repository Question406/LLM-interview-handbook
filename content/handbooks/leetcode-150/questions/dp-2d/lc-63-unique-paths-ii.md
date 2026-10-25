---
id: lc-63-unique-paths-ii
section: dp-2d
order: 3
level: A
title: LC 63 · 不同路径 II
quick: "LC 62 加障碍：障碍格的方案数为 $0$，其余格 $dp[i][j]$ 等于上方加左方，起点是障碍就直接返回 $0$。一维滚动时遇到障碍要把 `dp[j]` 置零，时间 $O(mn)$、空间 $O(n)$。"
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

## 题目描述

机器人位于一个 m 行 n 列网格的左上角，目标是到达右下角。每一步只能向右或向下移动一个格子。网格中的 1 表示不能进入的障碍，0 表示可走。求从起点到终点的不同合法路径数。

### 输入与输出

实现 `uniquePathsWithObstacles(obstacleGrid: List[List[int]]) -> int`。若起点、终点被障碍挡住，或不存在通路，返回 0；路径不能越出网格。

### 约束

- `1 <= m,n <= 100`，输入是矩形网格。
- 每个格子只可能是 0 或 1；题目保证路径数不超过 `2 * 10^9`。

### 示例

```text
输入：obstacleGrid = [[0,0,0],[0,1,0],[0,0,0]]
输出：2
```

中间的障碍阻止穿过中心的路线，剩余路径分别从网格上边或左边绕过。

## 解题思路与参考答案

## 题意

网格 `obstacleGrid` 里 `1` 是障碍、`0` 可走。从左上走到右下，只能向右或向下，求路径条数。

## 思路

这是 LC 62 加障碍，我会用网格 DP 加一维滚动。只能向右或向下，到达一格的路径数就等于从上方来的加从左方来的；障碍格方案数为 $0$，也不会往外贡献。起点是障碍的话答案就是 $0$。

拿 `[[0,0,0],[0,1,0],[0,0,0]]` 来说，第一行都是 $1$；第二行是 `1, 0, 1`，中间的障碍置 $0$；第三行是 `1, 1, 2`，右下角有 $2$ 条路。

用一维 `dp[j]` 时，本行遇到障碍就置 $0$，否则加上 `dp[j-1]`（左边）。障碍会切断前缀的可达性：第一行或第一列一旦出现障碍，后面整段都是 $0$。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert uniquePathsWithObstacles([[0, 0, 0], [0, 1, 0], [0, 0, 0]]) == 2
assert uniquePathsWithObstacles([[0, 1], [0, 0]]) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，额外空间 $O(n)$。

## 边界

起点是障碍时 `dp[0]=0`，后面全是 $0$。终点是障碍时该格被置 $0$，答案 $0$。第一行或第一列中途有障碍时，障碍及之后整段为 $0$，因为只能沿着边走过去。完全没有障碍就退化成 LC 62，方案数是组合数 $C(m+n-2, m-1)$。

## 追问

**没有障碍（LC 62）呢？**
照样滚动，`dp[j] += dp[j-1]`，初值全是 $1$。也可以直接算组合数，连乘时边乘边整除，避免溢出，时间 $O(\min(m,n))$。

```python
def uniquePaths(m, n):
    a, b = m + n - 2, min(m, n) - 1
    ans = 1
    for i in range(1, b + 1):
        ans = ans * (a - b + i) // i
    return ans
```

**最小路径和加上障碍呢？**
可走的格子仍取上、左较小者再加代价，障碍格不往外贡献。下面的代码用负数标记障碍，滚动时写成 $+\infty$；终点仍是 $\infty$ 说明没路，返回 $-1$。时间 $O(mn)$。

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

**路径数要取模吗？**
看题意。无障碍时 $C(m+n-2,m-1)$ 很快就超过 32 位，题目要求时每次加法都对 $10^9+7$ 取模，障碍置零后再加。Python 是无限精度整数，也可以最后再模，但滚动时就取模更稳。

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
