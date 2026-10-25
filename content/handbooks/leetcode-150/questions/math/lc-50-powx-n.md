---
id: lc-50-powx-n
section: math
order: 5
level: A
title: LC 50 · Pow(x, n)
quick: "用快速幂，按指数的二进制位来算，当前位为 1 就把结果乘上当前底数，每轮底数平方、指数右移。$n\\lt 0$ 时先取倒数再处理 $-n$；32 位整数的 $n=-2^{31}$ 不能直接取负，要先转成更宽的类型。"
tags:
  - Math
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 50. Pow(x, n)
    url: https://leetcode.cn/problems/powx-n/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定浮点数 x 和整数 n，计算 x 的 n 次幂。负指数表示对应正指数幂的倒数；指数为 0 时结果为 1。

### 接口与输出

实现 `myPow(x: float, n: int) -> float`，返回数值结果。n 是有符号整数，需要覆盖其整个合法范围。

### 合法输入与约束

`-100 < x < 100`，`-2^31 <= n <= 2^31-1`，且 `-10000 <= x^n <= 10000`。输入保证 x 非零，或者 n 为正数，因此不要求处理零的负次幂或 `0^0`。

### 示例

```text
输入：x = 2.00000, n = 10
输出：1024.00000
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/powx-n/description/)。

## 解题思路与参考答案

## 题意

计算 $x^n$。$n$ 是 32 位有符号整数，可以为负。

## 思路

我用快速幂，只要 $O(\log |n|)$ 次乘法，别连乘 $n$ 次。把 $n$ 看成二进制，当前位是 $1$ 就乘上此刻的底，底每轮平方，指数右移一位。

拿样例 $2^{10}$ 走一遍，$10$ 的二进制是 1010。最低位是 0，不乘，底变成 $2^2$；下一位是 1，结果乘上 $2^2$，底变成 $2^4$；再下一位是 0，底变成 $2^8$；最高位是 1，结果乘上 $2^8$，得到 $2^{10}=1024$。

$n\lt 0$ 时变成 $(1/x)^{-n}$。32 位里 $n=-2^{31}$ 时 `-n` 会溢出，要先把指数收到长整型，或者先处理一位再取负。Python 整数不会溢出，面试时我仍会主动提这一点。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert abs(myPow(2.00000, 10) - 1024.00000) < 1e-8
assert abs(myPow(2.10000, 3) - 9.26100) < 1e-8
assert abs(myPow(2.00000, -2) - 0.25000) < 1e-8
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log |n|)$，额外空间 $O(1)$。递归写法空间 $O(\log |n|)$。

## 边界

- $n=0$ 时是空乘积，返回 $1$；即使 $x=0$，按题意通常也返回 $1$。
- $x=0$ 且 $n\gt 0$ 时一直乘 $0$，答案是 $0$。
- $n$ 为负时先取倒数，再对 $|n|$ 做快速幂。

## 追问

**$n=-2^{31}$ 怎么处理？**
32 位有符号整数里 `-n` 会溢出。C++ 就把指数放进 `long long`，或者先消耗一位，$x^{-2^{31}}=(1/x)\cdot(1/x)^{2^{31}-1}$。Python 整数不溢出，但面试仍要提。

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

**矩阵快速幂、取模的幂怎么写？**
同一套二进制拆分，把 `ans *= x`、`x *= x` 换成矩阵乘法或者 `(a * b) % mod` 就行。矩阵幂用来加速线性递推，比如斐波那契可以做到 $O(\log n)$。

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
