---
id: lc-1137-n-th-tribonacci-number
section: dp-1d
order: 1
level: A
title: LC 1137 · 第 N 个泰波那契数
quick: >-
  $T_{i}=T_{i-1}+T_{i-2}+T_{i-3}$，初值 $T_0=0, T_1=T_2=1$。滚三个变量往前推即可。时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - DP
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1137. N-th Tribonacci Number
    url: https://leetcode.com/problems/n-th-tribonacci-number/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

泰波那契序列：$T_0=0$，$T_1=1$，$T_2=1$，对 $n\ge 0$ 有 $T_{n+3}=T_n+T_{n+1}+T_{n+2}$。给 $n$（$0\le n\le 37$），返回 $T_n$。题目保证答案在 32 位整数内。

## 思路

状态就是 $T_i$ 本身，转移 $T_i=T_{i-1}+T_{i-2}+T_{i-3}$。每一项只依赖前三项，所以不用开数组，用 `a, b, c` 表示 $T_{i-3}, T_{i-2}, T_{i-1}$，每步整体左移一格。

直接按定义递归会指数爆炸，因为同一个 $T_i$ 被重复算很多次；加记忆化能降到 $O(n)$，但滚动变量更省空间，也不用担心递归深度。

## 参考代码

```python
def tribonacci(n: int) -> int:
    if n == 0:
        return 0
    if n <= 2:
        return 1
    a, b, c = 0, 1, 1
    for _ in range(3, n + 1):
        a, b, c = b, c, a + b + c
    return c


if __name__ == "__main__":
    assert tribonacci(4) == 4
    assert tribonacci(25) == 1389537
    assert tribonacci(0) == 0
    assert tribonacci(1) == 1
    assert tribonacci(2) == 1
    assert tribonacci(3) == 2
    assert tribonacci(37) == 2082876103
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- $n=0$：返回 $0$，不要被 $T_1=T_2=1$ 带偏。
- $n=1, 2$：直接返回 $1$，循环不进。
- $n=37$：结果约 $2\times 10^9$，仍在 32 位有符号范围内；其他语言要注意别在中间多算一项溢出。

## 追问

- **$n$ 很大、结果取模怎么办？** 把转移写成 $3\times 3$ 矩阵：$(T_{i}, T_{i-1}, T_{i-2})^\top = M\,(T_{i-1}, T_{i-2}, T_{i-3})^\top$，$M$ 第一行全 $1$，下面两行是移位。快速幂求 $M^{n-2}$，时间 $O(27\log n)$。

```python
def tribonacciMatrix(n, mod=10**9 + 7):
    if n == 0:
        return 0
    if n <= 2:
        return 1

    def mul(x, y):
        return [
            [sum(x[i][k] * y[k][j] for k in range(3)) % mod for j in range(3)]
            for i in range(3)
        ]

    res = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    m = [[1, 1, 1], [1, 0, 0], [0, 1, 0]]
    p = n - 2
    while p:
        if p & 1:
            res = mul(res, m)
        m = mul(m, m)
        p >>= 1
    return (res[0][0] + res[0][1]) % mod
```

- **和斐波那契写法有什么区别？** 骨架一样，只是窗口从两个变量变成三个。面试里常先问斐波那契再问这题，考的是能不能把「只依赖前 $k$ 项」压成 $k$ 个变量。
