---
id: lc-70-climbing-stairs
section: dp-1d
order: 1
level: S
title: LC 70 · 爬楼梯
quick: >-
  每次 $1$ 或 $2$ 阶，$n$ 阶有多少种走法。$f(n)=f(n-1)+f(n-2)$，滚动两个变量即可。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - DP
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 70. 爬楼梯
    url: https://leetcode.cn/problems/climbing-stairs/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

爬 $n$ 阶楼梯，每次走 $1$ 或 $2$ 阶。问有多少种走法。

## 思路

最后一步只能从 $n-1$ 或 $n-2$ 过来，所以 $f(n)=f(n-1)+f(n-2)$，$f(1)=1$，$f(2)=2$。斐波那契。

数组可以滚成两个变量。递归不记忆会爆指数。面试先写清转移，再压缩空间。

## 参考代码

```python
def climbStairs(n: int) -> int:
    if n <= 2:
        return n
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b


if __name__ == "__main__":
    assert climbStairs(2) == 2
    assert climbStairs(3) == 3
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。矩阵快速幂可到 $O(\log n)$。

## 边界

- $n=1$：只有一种，走 $1$ 阶。
- $n=2$：$1+1$ 或直接 $2$，两种。

## 追问

- **一次最多走 $k$ 阶？** $f(n)=\sum_{i=1}^{\min(k,n)} f(n-i)$，$f(0)=1$。用长度为 $k$ 的滑动窗口维护最近 $k$ 项和，时间 $O(n)$。$k=2$ 时退回本题。

```python
def climbK(n, k):
    dp = [0] * (n + 1)
    dp[0] = 1
    window = 1
    for i in range(1, n + 1):
        dp[i] = window
        window += dp[i]
        if i >= k:
            window -= dp[i - k]
    return dp[n]
```

- **带障碍或最小代价（LC 746）？** 状态仍是「到达第 $i$ 阶」。最小代价：付 `cost[i]` 后从 $i-1$ 或 $i-2$ 过来，滚两个变量；顶层不必再付费，答案是最后两个状态的较小。有障碍则对应位置不可达，跳过转移。

```python
def minCostClimbingStairs(cost):
    a = b = 0
    for c in cost:
        a, b = b, c + min(a, b)
    return min(a, b)
```
