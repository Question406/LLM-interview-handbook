---
id: lc-70-climbing-stairs
section: dp-1d
order: 1
level: S
title: LC 70 · 爬楼梯
quick: "最后一步只能从 $n-1$ 或 $n-2$ 阶上来，所以 $f(n)=f(n-1)+f(n-2)$，就是斐波那契。滚动两个变量即可，时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - DP
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 70. 爬楼梯
    url: https://leetcode.cn/problems/climbing-stairs/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

一段楼梯有 n 级。你从楼梯下方出发，每一步只能向上走 1 级或 2 级，问恰好到达第 n 级共有多少种不同的步长序列。步长相同但出现顺序不同的序列也算不同走法。

### 输入与输出

实现 `climbStairs(n) -> int`，返回走法总数，不需要返回所有步长序列。

### 约束与约定

- `1 <= n <= 45`。

### 示例

```text
输入：n = 2
输出：2
```

n=2 时可以走 [1,1] 或 [2]，所以有两种走法。

[官方原题与完整题面](https://leetcode.com/problems/climbing-stairs/description/)。

## 解题思路与参考答案

## 题意

爬 $n$ 阶楼梯，每次走 $1$ 或 $2$ 阶，问有多少种走法。

## 思路

这题就是斐波那契。最后一步要么跨 $1$ 阶、从 $n-1$ 上来，要么跨 $2$ 阶、从 $n-2$ 上来，两类走法不重叠，所以 $f(n)=f(n-1)+f(n-2)$，$f(1)=1$，$f(2)=2$。比如 $n=3$，从第 $2$ 阶上来有 $2$ 种，从第 $1$ 阶上来有 $1$ 种，一共 $3$ 种。

转移只用前两项，数组可以滚成两个变量。直接递归不加记忆会是指数级。面试时先写清转移，再压缩空间。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert climbStairs(2) == 2
assert climbStairs(3) == 3
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。用矩阵快速幂可以做到 $O(\log n)$。

## 边界

$n=1$ 只有一种，走 $1$ 阶。$n=2$ 有两种，$1+1$ 或者直接走 $2$。

## 追问

**一次最多走 $k$ 阶呢？**
$f(n)=\sum_{i=1}^{\min(k,n)} f(n-i)$，$f(0)=1$。用长度为 $k$ 的滑动窗口维护最近 $k$ 项的和，时间 $O(n)$。$k=2$ 时就回到本题。

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

**带障碍，或者求最小代价（LC 746）呢？**
状态仍然是「到达第 $i$ 阶」。最小代价版付 `cost[i]` 后从 $i-1$ 或 $i-2$ 过来，同样滚两个变量；顶层不用再付费，答案是最后两个状态里较小的。有障碍的话，对应台阶不可达，跳过它的转移。

```python
def minCostClimbingStairs(cost):
    a = b = 0
    for c in cost:
        a, b = b, c + min(a, b)
    return min(a, b)
```
