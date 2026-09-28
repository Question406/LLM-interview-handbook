---
id: lc-746-min-cost-climbing-stairs
section: dp-1d
order: 2
level: A
title: LC 746 · 使用最小花费爬楼梯
quick: >-
  $dp[i]$ 表示站到第 $i$ 级（还没付这级的费）的最小花费，$dp[0]=dp[1]=0$，$dp[i]=\min(dp[i-1]+cost[i-1],\,dp[i-2]+cost[i-2])$，答案
  $dp[n]$。滚两个变量，时间 $O(n)$，额外空间 $O(1)$。
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

## 题意

数组 `cost`，`cost[i]` 是从第 $i$ 级台阶往上爬要付的费用。付完可以爬 $1$ 级或 $2$ 级。可以从下标 $0$ 或 $1$ 开始。楼顶在下标 $n$（数组外一格），求到达楼顶的最小总花费。$2\le n\le 1000$。

## 思路

先把状态定义说死：$dp[i]$ 是「站到第 $i$ 级、还没付第 $i$ 级费用」时已经花掉的最小值。可以免费从 $0$ 或 $1$ 起步，所以 $dp[0]=dp[1]=0$。到第 $i$ 级只能从 $i-1$ 付 `cost[i-1]` 上来，或从 $i-2$ 付 `cost[i-2]` 上来：

$dp[i]=\min(dp[i-1]+cost[i-1],\ dp[i-2]+cost[i-2])$，答案是 $dp[n]$。

这题最容易错在定义含糊：有人把 $dp[i]$ 定义成「含第 $i$ 级费用」，那答案要写成 $\min(dp[n-1], dp[n-2])$，两种都对，但混着写就会多算或少算一级。我会先讲清楚楼顶是 $n$、费用什么时候付。

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

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- $n=2$：直接从较便宜的那级一步跨两级到顶，答案 $\min(cost[0], cost[1])$。
- 费用含 $0$：转移不变，$0$ 那级相当于免费跳板。
- 楼顶是下标 $n$ 而不是 $n-1$：写成 `dp[n-1]` 会漏掉最后一次跨越。

## 追问

- **要输出具体踩了哪些台阶？** 保留整张 `dp` 表，从 $n$ 往回看：若 $dp[i]=dp[i-1]+cost[i-1]$ 就说明从 $i-1$ 上来，否则从 $i-2$。退到 $0$ 或 $1$ 为止，反转得到路径。

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

- **一次可以爬 $1$ 到 $k$ 级？** 转移变成 $dp[i]=\min_{1\le j\le k}(dp[i-j]+cost[i-j])$，朴素 $O(nk)$；用单调队列维护窗口内 $dp[t]+cost[t]$ 的最小值可降到 $O(n)$。
