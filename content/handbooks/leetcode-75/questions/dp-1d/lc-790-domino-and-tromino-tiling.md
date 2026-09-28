---
id: lc-790-domino-and-tromino-tiling
section: dp-1d
order: 4
level: A
title: LC 790 · 多米诺和托米诺平铺
quick: >-
  两个状态：$f[i]$ 是 $2\times i$ 铺满的方案数，$p[i]$ 是前 $i-1$ 列铺满、第 $i$ 列只铺了一格。$f[i]=f[i-1]+f[i-2]+2p[i-1]$，$p[i]=p[i-1]+f[i-2]$，化简得
  $f[n]=2f[n-1]+f[n-3]$。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 790. Domino and Tromino Tiling
    url: https://leetcode.com/problems/domino-and-tromino-tiling/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

有两种砖：$2\times 1$ 的多米诺（可旋转）和 L 形的托米诺（占 $3$ 格，可旋转）。求铺满 $2\times n$ 面板的方案数，对 $10^9+7$ 取模。$1\le n\le 1000$。两种铺法只要有一对相邻格子一个被同一块砖覆盖、另一个不是，就算不同。

## 思路

按列从左往右铺，看最右边的边界形状。只会出现两种：右边齐平（$f$），或者最后一列只铺了上格或下格、凸出一个角（$p$，上下对称，只算一种再乘 $2$）。

- $f[i]$：最后放一块竖多米诺，来自 $f[i-1]$；最后两块横多米诺叠放，来自 $f[i-2]$；最后放一块托米诺把凸角补平，来自 $p[i-1]$，上凸下凸各一种，所以是 $2p[i-1]$。合起来 $f[i]=f[i-1]+f[i-2]+2p[i-1]$。
- $p[i]$（第 $i$ 列只铺一格）：在凸角那行补一块横多米诺，来自另一方向的凸角 $p[i-1]$；或者直接放一块托米诺从齐平的 $f[i-2]$ 长出来。$p[i]=p[i-1]+f[i-2]$。

初值 $f[0]=1$（空板一种），$f[1]=1$，$p[1]=0$。把 $p$ 消掉可得 $f[n]=2f[n-1]+f[n-3]$，结果一样。直接背化简式容易讲不清来源，我会先讲两状态，再顺手给出化简式。

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

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- $n=1$：只能一块竖多米诺，答案 $1$。
- $n=2$：两竖或两横，托米诺铺不满 $2\times 2$，答案 $2$。
- 取模：每步都要取，$n=1000$ 时不取模数值会非常大。

## 追问

- **$f[n]=2f[n-1]+f[n-3]$ 怎么推？** 由 $f[i]=f[i-1]+f[i-2]+2p[i-1]$ 与 $f[i-1]=f[i-2]+f[i-3]+2p[i-2]$ 相减，再代入 $p[i-1]-p[i-2]=f[i-3]$，得 $f[i]-f[i-1]=f[i-1]+f[i-3]$。

- **$n$ 到 $10^{18}$？** 线性递推用矩阵快速幂：状态向量 $(f_i, f_{i-1}, f_{i-2})$，转移矩阵第一行 $(2,0,1)$，其余两行移位，$O(\log n)$。

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
