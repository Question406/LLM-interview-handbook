---
id: lc-790-domino-and-tromino-tiling
section: dp-1d
order: 4
level: A
title: LC 790 · 多米诺和托米诺平铺
quick: >-
  用两个状态：$f[i]$ 是 $2\times i$ 铺满的方案数，$p[i]$ 是前 $i-1$ 列铺满、第 $i$
  列只铺一格。$f[i]=f[i-1]+f[i-2]+2p[i-1]$，$p[i]=p[i-1]+f[i-2]$，消掉 $p$ 得
  $f[n]=2f[n-1]+f[n-3]$。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 790. Domino and Tromino Tiling
    url: 'https://leetcode.com/problems/domino-and-tromino-tiling/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

有一个 2 行 n 列的长方形棋盘，以及数量不限的两类砖：覆盖两个相邻格子的 2×1 多米诺，和覆盖三个格子的 L 形托米诺。砖可以旋转。求恰好铺满棋盘的不同铺法数量，不能重叠、越界或留下空格。只要格子属于同一块砖的关系有所不同，就算不同铺法；交换两块同形砖的编号不算新方案。

### 输入与输出

实现 `numTilings(n) -> int`，返回铺法总数对 `1000000007` 取模的结果。输入是棋盘列数 n，行数固定为 2。

### 约束与约定

- `1 <= n <= 1000`。
- 允许两种砖的所有旋转方向，每块砖必须完整放在棋盘内。

### 示例

```text
输入：n = 3
输出：5
```

2×3 棋盘有五种不同的完整铺法，因此输出 5。

[官方原题与完整题面](https://leetcode.com/problems/domino-and-tromino-tiling/description/)。

## 解题思路与参考答案

## 题意

有两种砖：$2\times 1$ 的多米诺（可旋转）和 L 形的托米诺（占 $3$ 格，可旋转）。求铺满 $2\times n$ 面板的方案数，对 $10^9+7$ 取模。$1\le n\le 1000$。两种铺法只要有一对相邻格子一个被同一块砖覆盖、另一个不是，就算不同。

## 思路

我按列从左往右铺，用 rightmost frontier shape 当状态。frontier 只会有两种形状：右边齐平，记作 $f$；或者最后一列只铺了上格或下格、凸出一个角，记作 $p$。上凸和下凸对称，只算一种，用到时乘 $2$。

先看 $f[i]$ 从哪来。最后放一块竖多米诺，来自 $f[i-1]$；最后两块横多米诺叠着放，来自 $f[i-2]$；最后放一块托米诺把凸角补平，来自 $p[i-1]$，上凸下凸各一种，所以是 $2p[i-1]$。合起来 $f[i]=f[i-1]+f[i-2]+2p[i-1]$。

再看 $p[i]$，也就是第 $i$ 列只铺了一格。可以在凸角那一行补一块横多米诺，从另一方向的凸角 $p[i-1]$ 过来；也可以直接放一块托米诺，从齐平的 $f[i-2]$ 长出来。所以 $p[i]=p[i-1]+f[i-2]$。

初值 $f[0]=1$（空板算一种），$f[1]=1$，$p[1]=0$。拿 $n=3$ 验一下：$p[2]=p[1]+f[0]=1$，$f[3]=f[2]+f[1]+2p[2]=2+1+2=5$，和样例一致。

把 $p$ 消掉可以得到 $f[n]=2f[n-1]+f[n-3]$，结果一样。只背化简式的话讲不清来源，我会先讲两个状态，再顺手给出化简式。

## 参考代码

```python
MOD = 10**9 + 7


def numTilings(n: int) -> int:
    if n <= 2:
        return n
    f_prev2, f_prev1 = 1, 2
    p_prev1 = 1
    for _ in range(3, n + 1):
        f_cur = (f_prev1 + f_prev2 + 2 * p_prev1) % MOD
        p_cur = (p_prev1 + f_prev2) % MOD
        f_prev2, f_prev1, p_prev1 = f_prev1, f_cur, p_cur
    return f_prev1


def numTilingsSimple(n: int) -> int:
    f = [1, 1, 2]
    for i in range(3, n + 1):
        f.append((2 * f[i - 1] + f[i - 3]) % MOD)
    return f[n]


if __name__ == "__main__":
    assert numTilings(3) == 5
    assert numTilings(1) == 1
    assert numTilings(2) == 2
    assert numTilings(4) == 11
    assert numTilings(5) == 24
    for k in range(1, 200):
        assert numTilings(k) == numTilingsSimple(k)
    assert numTilings(1000) == numTilingsSimple(1000)
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert numTilings(3) == 5
assert numTilings(1) == 1
assert numTilings(2) == 2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

$n=1$ 只能放一块竖多米诺，答案 $1$。

$n=2$ 是两竖或两横，托米诺铺不满 $2\times 2$，答案 $2$。

取模每一步都要做，$n=1000$ 时不取模数值会非常大。

## 追问

**$f[n]=2f[n-1]+f[n-3]$ 是怎么推出来的？**
把 $f[i]=f[i-1]+f[i-2]+2p[i-1]$ 和 $f[i-1]=f[i-2]+f[i-3]+2p[i-2]$ 相减，再代入 $p[i-1]-p[i-2]=f[i-3]$，就得到 $f[i]-f[i-1]=f[i-1]+f[i-3]$。

**$n$ 到 $10^{18}$ 怎么办？**
线性递推上矩阵快速幂。状态向量取 $(f_i, f_{i-1}, f_{i-2})$，转移矩阵第一行是 $(2,0,1)$，其余两行是移位，时间 $O(\log n)$。

```python
def numTilingsMatrix(n, mod=10**9 + 7):
    if n <= 2:
        return n

    def mul(x, y):
        return [
            [sum(x[i][k] * y[k][j] for k in range(3)) % mod for j in range(3)]
            for i in range(3)
        ]

    res = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    m = [[2, 0, 1], [1, 0, 0], [0, 1, 0]]
    p = n - 2
    while p:
        if p & 1:
            res = mul(res, m)
        m = mul(m, m)
        p >>= 1
    return (res[0][0] * 2 + res[0][1] * 1 + res[0][2] * 1) % mod
```
