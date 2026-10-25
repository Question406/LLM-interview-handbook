---
id: lc-1137-n-th-tribonacci-number
section: dp-1d
order: 1
level: A
title: LC 1137 · 第 N 个泰波那契数
quick: "按 $T_{i}=T_{i-1}+T_{i-2}+T_{i-3}$ 往前推，初值 $T_0=0, T_1=T_2=1$。每项只依赖前三项，滚三个变量就够，时间 $O(n)$，额外空间 $O(1)$。"
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

## 题目描述

泰波那契数列从 `T0=0`、`T1=1`、`T2=1` 开始，后续每一项等于前面三项的和，即对 n>=0 有 `T(n+3)=Tn+T(n+1)+T(n+2)`。给定非负整数 n，返回数列的第 n 项，下标从0开始。

### 输入与输出

实现 `tribonacci(n) -> int`。只返回对应的一个整数，不需要返回从第0项开始的整个序列。

### 约束

- `0 <= n <= 37`。
- 题目保证结果不超过 `2^31-1`，可由32位有符号整数表示。

### 示例

```text
输入：n = 4
输出：4
```

[LeetCode 原题](https://leetcode.com/problems/n-th-tribonacci-number/description/)

## 解题思路与参考答案

## 题意

泰波那契序列：$T_0=0$，$T_1=1$，$T_2=1$，对 $n\ge 0$ 有 $T_{n+3}=T_n+T_{n+1}+T_{n+2}$。给 $n$（$0\le n\le 37$），返回 $T_n$。题目保证答案在 32 位整数内。

## 思路

我直接按递推往前算，用三个变量滚动。状态就是 $T_i$ 本身，转移 $T_i=T_{i-1}+T_{i-2}+T_{i-3}$，每一项只看前三项，所以不用开数组：`a, b, c` 分别是 $T_{i-3}, T_{i-2}, T_{i-1}$，每步整体往左挪一格。

拿 $n=4$ 走一遍：一开始 `a, b, c = 0, 1, 1`；算 $T_3$ 变成 `1, 1, 2`；算 $T_4$ 变成 `1, 2, 4`，返回 `4`。

按定义直接递归会指数爆炸，同一个 $T_i$ 被算很多遍。加记忆化能降到 $O(n)$，滚动变量更省空间，也不用担心递归深度。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert tribonacci(4) == 4
assert tribonacci(25) == 1389537
assert tribonacci(0) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

$n=0$ 要返回 $0$，别被 $T_1=T_2=1$ 带偏。

$n=1$ 和 $n=2$ 直接返回 $1$，循环不进。

$n=37$ 时结果约 $2\times 10^9$，还在 32 位有符号范围内。换成别的语言写，要留意别在中间多算一项导致溢出。

## 追问

**$n$ 很大、结果要取模怎么办？**
把转移写成 $3\times 3$ 矩阵：$(T_{i}, T_{i-1}, T_{i-2})^\top = M\,(T_{i-1}, T_{i-2}, T_{i-3})^\top$，$M$ 第一行全是 $1$，下面两行是移位。用快速幂求 $M^{n-2}$，时间 $O(27\log n)$。

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

**和斐波那契的写法有什么区别？**
骨架一样，窗口从两个变量变成三个。面试里常先问斐波那契再问这题，看的是能不能把「只依赖前 $k$ 项」压成 $k$ 个变量。
