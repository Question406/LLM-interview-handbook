---
id: lc-322-coin-change
section: dp-1d
order: 4
level: S
title: LC 322 · 零钱兑换
quick: >-
  完全背包求最少枚数。$dp[x]=\min_c(dp[x-c]+1)$，$dp[0]=0$，其余初始化成
  $+\infty$。凑不出返回 $-1$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 322. 零钱兑换
    url: https://leetcode.cn/problems/coin-change/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

硬币面值 `coins`（无限枚），凑出金额 `amount` 的最少枚数。无法凑出返回 $-1$。

## 思路

$dp[x]$：凑出 $x$ 的最少枚数。$dp[0]=0$。对每个金额 $x$，枚举硬币 $c\le x$，取 $dp[x-c]+1$ 的最小。硬币无限，属于完全背包，金额在外或硬币在外都可以，只要是「先小后大」。

初始化成 `amount+1` 当无穷大。最后若仍是无穷大则 $-1$。贪心按面值从大到小在非典型币制下是错的。白板我先讲「完全背包最小值」。

## 参考代码

```python
from typing import List


def coinChange(coins: List[int], amount: int) -> int:
    inf = amount + 1
    dp = [inf] * (amount + 1)
    dp[0] = 0
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x:
                dp[x] = min(dp[x], dp[x - c] + 1)
    return dp[amount] if dp[amount] < inf else -1


if __name__ == "__main__":
    assert coinChange([1, 2, 5], 11) == 3
    assert coinChange([2], 3) == -1
    assert coinChange([1], 0) == 0
    print("ok")
```

## 复杂度

时间 $O(\mathrm{amount}\cdot |coins|)$，额外空间 $O(\mathrm{amount})$。

## 边界

- `amount=0`：不需要硬币，返回 $0$。
- 所有面值大于金额：`dp[amount]` 保持无穷大，返回 $-1$。
- 凑不出（如 `[2]` 凑 $3$）：同上，不能用贪心硬凑。

## 追问

- **方案数（LC 518）？** 完全背包求组合数。$dp[0]=1$。硬币在外、金额在内正向更新，保证每种组合只计一次；若金额在外、硬币在内，计的是排列。时间 $O(\mathrm{amount}\cdot |coins|)$。

```python
def change(amount, coins):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for x in range(c, amount + 1):
            dp[x] += dp[x - c]
    return dp[amount]
```

- **为什么不能纯贪心？** 面值不保证典。`[1,3,4]` 凑 $6$：贪心从大到小得 $4+1+1$ 三枚，最优是 $3+3$ 两枚。只有「标准币制」一类才可贪心。白板我用反例否掉，再写完全背包。

```python
def greedy_wrong(coins, amount):
    coins = sorted(coins, reverse=True)
    cnt = 0
    for c in coins:
        cnt += amount // c
        amount %= c
    return cnt if amount == 0 else -1
# greedy_wrong([1, 3, 4], 6) == 3，而最优是 2
```
