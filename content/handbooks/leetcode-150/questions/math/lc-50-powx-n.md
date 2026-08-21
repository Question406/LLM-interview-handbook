---
id: lc-50-powx-n
section: math
order: 5
level: A
title: LC 50 · Pow(x, n)
quick: >-
  快速幂：奇数乘一次当前底，底自乘，指数右移。$n\lt 0$ 先取倒数再对 $-n$ 做。注意
  $n=-2^{31}$ 在 32 位里取负会溢出。
tags:
  - Math
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 50. Pow(x, n)
    url: https://leetcode.cn/problems/powx-n/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

计算 $x^n$。$n$ 是 32 位有符号整数，可为负。

## 思路

快速幂：把 $n$ 看成二进制。当前位是 $1$ 就乘上此刻的底；底每次平方，指数右移。$O(\log |n|)$ 次乘法，不要连乘 $n$ 次。

$n\lt 0$ 变成 $(1/x)^{-n}$。32 位里 $n=-2^{31}$ 时 `-n` 溢出，先把指数收到长整型，或先处理一位再取负。Python 整数不溢出，面试仍要主动提这点。

## 参考代码

```python
def myPow(x: float, n: int) -> float:
    if n < 0:
        x = 1.0 / x
        n = -n
    ans = 1.0
    while n:
        if n & 1:
            ans *= x
        x *= x
        n >>= 1
    return ans


if __name__ == "__main__":
    assert abs(myPow(2.00000, 10) - 1024.00000) < 1e-8
    assert abs(myPow(2.10000, 3) - 9.26100) < 1e-8
    assert abs(myPow(2.00000, -2) - 0.25000) < 1e-8
    print("ok")
```

## 复杂度

时间 $O(\log |n|)$，额外空间 $O(1)$。递归写法空间 $O(\log |n|)$。

## 边界

- $n=0$：空乘积，返回 $1$（即使 $x=0$，按题意通常也是 $1$）。
- $x=0$ 且 $n\gt 0$：一直乘 $0$，答案 $0$。
- $n$ 为负：先取倒数再对 $|n|$ 做快速幂。

## 追问

- **$n=-2^{31}$？** 32 位有符号里 `-n` 溢出。Python 整数不溢出，面试仍要提。C++ 把指数放进 `long long`，或先消耗一位：$x^{-2^{31}}=(1/x)\cdot(1/x)^{2^{31}-1}$。

```python
def myPowSafe(x, n):
    if n == 0:
        return 1.0
    if n < 0:
        x = 1.0 / x
        if n == -(1 << 31):
            return x * myPowSafe(x, (1 << 31) - 1)
        n = -n
    ans = 1.0
    while n:
        if n & 1:
            ans *= x
        x *= x
        n >>= 1
    return ans
```

- **矩阵快速幂 / 模意义下幂？** 同一套二进制拆分。把 `ans *= x`、`x *= x` 换成矩阵乘法或 `(a * b) % mod`。矩阵幂用来加速线性递推，如斐波那契 $O(\log n)$。

```python
def mod_pow(a, n, mod):
    ans = 1
    a %= mod
    while n:
        if n & 1:
            ans = ans * a % mod
        a = a * a % mod
        n >>= 1
    return ans

def mat_mul(A, B):
    n = len(A)
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            aik = A[i][k]
            if aik == 0:
                continue
            for j in range(n):
                C[i][j] += aik * B[k][j]
    return C

def mat_pow(M, n):
    k = len(M)
    ans = [[int(i == j) for j in range(k)] for i in range(k)]
    while n:
        if n & 1:
            ans = mat_mul(ans, M)
        M = mat_mul(M, M)
        n >>= 1
    return ans
```
