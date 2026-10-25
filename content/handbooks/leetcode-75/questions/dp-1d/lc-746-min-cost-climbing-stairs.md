---
id: lc-746-min-cost-climbing-stairs
section: dp-1d
order: 2
level: A
title: LC 746 · 使用最小花费爬楼梯
quick: "令 $dp[i]$ 为站到第 $i$ 级、还没付这级费用时的最小花费，$dp[0]=dp[1]=0$，$dp[i]=\\min(dp[i-1]+cost[i-1],\\,dp[i-2]+cost[i-2])$，答案是 $dp[n]$。滚两个变量，时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - DP
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 746. Min Cost Climbing Stairs
    url: https://leetcode.com/problems/min-cost-climbing-stairs/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

楼梯第 i 级的费用为 cost[i]。站在某一级台阶并支付它的费用后，可以向上走一级或两级。允许从下标 0 或下标 1 的台阶开始；楼顶位于下标 n，恰好在数组最后一项之后。求到达楼顶的最小累计费用。

### 接口与输出

实现 `minCostClimbingStairs(cost: List[int]) -> int`。只为实际踩到并离开的收费台阶付费，楼顶本身没有额外费用；返回最小总费用。

### 合法输入与约束

`2 <= len(cost) <= 1000`，`0 <= cost[i] <= 999`。跳过的台阶不收费，费用为 0 的台阶合法。

### 示例

```text
输入：cost = [10,15,20]
输出：15
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/min-cost-climbing-stairs/description/)。

## 解题思路与参考答案

## 题意

数组 `cost`，`cost[i]` 是从第 $i$ 级台阶往上爬要付的费用。付完可以爬 $1$ 级或 $2$ 级。可以从下标 $0$ 或 $1$ 开始。楼顶在下标 $n$（数组外一格），求到达楼顶的最小总花费。$2\le n\le 1000$。

## 思路

我会用一维动态规划，先明确费用是在离开台阶时支付的。$dp[i]$ 表示「站到第 $i$ 级、还没付第 $i$ 级费用」时已经花掉的最小值。可以免费从 $0$ 或 $1$ 起步，所以 $dp[0]=dp[1]=0$。到第 $i$ 级只有两条路：从 $i-1$ 付 `cost[i-1]` 上来，或者从 $i-2$ 付 `cost[i-2]` 上来。

$dp[i]=\min(dp[i-1]+cost[i-1],\ dp[i-2]+cost[i-2])$，答案是 $dp[n]$。

拿 `[10,15,20]` 走一遍：$dp[2]=\min(0+15, 0+10)=10$；$dp[3]=\min(10+20, 0+15)=15$，也就是从第 $1$ 级付 15 直接跨两级到顶。

这题最容易错在定义含糊。也有人把 $dp[i]$ 定义成「含第 $i$ 级费用」，那答案就要写成 $\min(dp[n-1], dp[n-2])$。两种都对，混着写就会多算或少算一级，所以我会先讲清楚楼顶是 $n$、费用什么时候付。

## 参考代码

```python
from typing import List


def minCostClimbingStairs(cost: List[int]) -> int:
    prev2 = prev1 = 0
    for i in range(2, len(cost) + 1):
        prev2, prev1 = prev1, min(prev1 + cost[i - 1], prev2 + cost[i - 2])
    return prev1


if __name__ == "__main__":
    assert minCostClimbingStairs([10, 15, 20]) == 15
    assert minCostClimbingStairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6
    assert minCostClimbingStairs([0, 0]) == 0
    assert minCostClimbingStairs([5, 3]) == 3
    assert minCostClimbingStairs([0, 1, 2, 2]) == 2
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert minCostClimbingStairs([10, 15, 20]) == 15
assert minCostClimbingStairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]) == 6
assert minCostClimbingStairs([0, 0]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

$n=2$ 时，从较便宜的那级一步跨两级到顶，答案 $\min(cost[0], cost[1])$。

费用里有 $0$ 也不影响转移，那级就相当于免费跳板。

楼顶在下标 $n$，写成 `dp[n-1]` 会漏掉最后一次跨越。

## 追问

**要输出具体踩了哪些台阶呢？**
保留整张 `dp` 表，从 $n$ 往回看：如果 $dp[i]=dp[i-1]+cost[i-1]$，说明是从 $i-1$ 上来的，否则是从 $i-2$。退到 $0$ 或 $1$ 为止，反转一下就是路径。

```python
def minCostPath(cost):
    n = len(cost)
    dp = [0] * (n + 1)
    for i in range(2, n + 1):
        dp[i] = min(dp[i - 1] + cost[i - 1], dp[i - 2] + cost[i - 2])
    path, i = [], n
    while i > 1:
        if dp[i] == dp[i - 1] + cost[i - 1]:
            i -= 1
        else:
            i -= 2
        path.append(i)
    return dp[n], path[::-1]
```

**一次可以爬 $1$ 到 $k$ 级呢？**
转移变成 $dp[i]=\min_{1\le j\le k}(dp[i-j]+cost[i-j])$，朴素做法 $O(nk)$。用单调队列维护窗口里 $dp[t]+cost[t]$ 的最小值，可以降到 $O(n)$。
