---
id: lc-62-unique-paths
section: dp-multi
order: 1
level: S
title: LC 62 · 不同路径
quick: "每个格子只能从上方或左侧到达，所以 $dp[i][j]=dp[i-1][j]+dp[i][j-1]$，第一行第一列都是 $1$。只留一行状态，用 `dp[j] += dp[j-1]` 更新，时间 $O(mn)$，额外空间 $O(n)$；也可以直接算组合数 $\\binom{m+n-2}{m-1}$。"
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

## 题目描述

一个机器人从 m 行 n 列网格的左上角出发，要走到右下角。每一步只能向右或向下移动一个格子，网格中没有障碍。求不同路径的总条数；只要某一步经过的位置不同，就视为不同路径。

### 输入与输出

实现 `uniquePaths(m: int, n: int) -> int`，返回路径数。m 是行数，n 是列数；单个格子的起点和终点相同，对应一条无需移动的路径。

### 约束

- `1 <= m,n <= 100`。
- 题目保证结果不超过 `2 * 10^9`。

### 示例

```text
输入：m = 3, n = 7
输出：28
```

## 解题思路与参考答案

## 题意

$m\times n$ 网格，机器人从左上角出发，每步只能向右或向下，走到右下角。求不同路径数。$1\le m, n\le 100$，答案不超过 $2\times 10^9$。

## 思路

我用网格 DP，因为走到某格的最后一步只有两种来路，而且互不重叠。$dp[i][j]$ 是走到格子 $(i,j)$ 的路径数，最后一步要么从上方下来，要么从左边过来，两类不重不漏：

$dp[i][j]=dp[i-1][j]+dp[i][j-1]$，第一行、第一列都只有一条路，填 $1$。

拿 $3\times 2$ 走一遍：第一行是 `[1, 1]`；第二行 `dp[1]` 加上左边的 1，变成 `[1, 2]`；第三行再加一次，变成 `[1, 3]`，答案 3。

可以看到每行只依赖上一行和本行左边，所以一维数组从左往右做 `dp[j] += dp[j-1]` 就够了：加之前的 `dp[j]` 是上一行，`dp[j-1]` 已经是本行。

换个角度看，总共要走 $m-1$ 次下、$n-1$ 次右，路径数就是在 $m+n-2$ 步里挑哪几步向下，也就是 $\binom{m+n-2}{m-1}$。DFS 暴力枚举路径是指数级，不考虑。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert uniquePaths(3, 7) == 28
assert uniquePaths(3, 2) == 3
assert uniquePaths(1, 1) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，额外空间 $O(n)$。组合数写法时间 $O(\min(m,n))$，额外空间 $O(1)$。

## 边界

$m=1$ 或 $n=1$ 时只有一条直线路径，答案是 $1$。

$m$ 和 $n$ 互换答案不变，可以让一维数组取较短的那一边。

手算组合数时要边乘边除，每步乘完马上整除，免得中间结果溢出或者出现小数。

## 追问

**网格里有障碍怎么办（LC 63）？**
障碍格的 $dp$ 为 $0$，其余转移不变。第一行第一列不能再直接填 $1$，遇到障碍之后全是 $0$。一维写法里把起点设成 $1$，遇到障碍把 `dp[j]` 清零，就能统一处理。

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

**不用库函数怎么算组合数？**
取 $k=\min(m,n)-1$，从 $i=1$ 乘到 $k$，每步 `res = res * (m + n - 2 - k + i) // i`。每一步的中间值本身都是某个组合数，所以整除不会丢精度。

```python
def uniquePathsComb(m, n):
    k = min(m, n) - 1
    total = m + n - 2
    res = 1
    for i in range(1, k + 1):
        res = res * (total - k + i) // i
    return res
```
