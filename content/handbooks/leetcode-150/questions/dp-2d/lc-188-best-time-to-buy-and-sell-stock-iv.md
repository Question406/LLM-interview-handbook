---
id: lc-188-best-time-to-buy-and-sell-stock-iv
section: dp-2d
order: 8
level: A
title: LC 188 · 买卖股票的最佳时机 IV
quick: >-
  最多 $k$ 笔。`buy[t]` / `sell[t]` 表示第 $t$ 笔的成本与利润。若 $k\ge n/2$，一笔最多跨两天，退化为无限次：把所有上涨段加起来。
tags:
  - DP
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 188. 买卖股票的最佳时机 IV
    url: https://leetcode.cn/problems/best-time-to-buy-and-sell-stock-iv/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

股价 `prices`，最多完成 $k$ 笔交易。求最大利润。一笔仍是先买后卖。

## 思路

LC 123 的推广。`buy[t]`、`sell[t]` 分别是完成第 $t$ 笔买入后的净成本、卖出后的利润。对每个价格，从 $t=1..k$ 更新：

`buy[t] = min(buy[t], p - sell[t-1])`，`sell[t] = max(sell[t], p - buy[t])`。

$k$ 很大时（$k \ge n/2$），限制不再起作用：任意上涨都可以单独成交，退化成无限次，累加 `max(prices[i]-prices[i-1], 0)`。否则 DP 是 $O(nk)$，不剪会超时。

## 参考代码

```python
from typing import List


def maxProfit(k: int, prices: List[int]) -> int:
    n = len(prices)
    if n < 2 or k == 0:
        return 0
    if k >= n // 2:
        return sum(max(prices[i] - prices[i - 1], 0) for i in range(1, n))
    buy = [10**18] * (k + 1)
    sell = [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            buy[t] = min(buy[t], p - sell[t - 1])
            sell[t] = max(sell[t], p - buy[t])
    return sell[k]


if __name__ == "__main__":
    assert maxProfit(2, [2, 4, 1]) == 2
    assert maxProfit(2, [3, 2, 6, 5, 0, 3]) == 7
    print("ok")
```

## 复杂度

时间 $O(nk)$，额外空间 $O(k)$。$k\ge n/2$ 时时间 $O(n)$。

## 边界

- $k=0$ 或 $n \lt 2$：做不成一笔，直接 $0$。
- 单调下跌：所有 `sell[t]` 停在 $0$。
- $k=1$：只更新一对 `buy/sell`，退化为「最低买入、最高卖出」，即 LC 121。独立卡见 `lc-121-best-time-to-buy-and-sell-stock`。

## 追问

- **为什么 $k \ge n/2$ 等于无限次？** 一笔至少占一个买日和一个卖日，最多 $\lfloor n/2\rfloor$ 笔能成交。$k$ 再大也挤不进更多交易，限制失效。此时把所有相邻正差加上即可，不必再跑 $O(nk)$。

```python
def maxProfit_unlimited(prices):
    return sum(max(prices[i] - prices[i - 1], 0) for i in range(1, len(prices)))
```

- **有冷冻期（LC 309）？** 卖出后必须空仓一天才能再买。三个变量：`hold` 持股，`sold` 今天刚卖，`rest` 已过冷冻的空仓。转移：`hold` 来自继续持有或 `rest - p`；`sold = hold + p`；`rest` 取「继续空仓」与「昨天刚卖」的较大者。返回 `max(sold, rest)`。

```python
def maxProfit_cooldown(prices):
    hold, sold, rest = -10**18, 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)
```

- **有手续费（LC 714）？** 无限次，但每笔卖出扣 `fee`。`hold` 为持股最大利润，`cash` 为空仓。每天 `hold = max(hold, cash - p)`，`cash = max(cash, hold + p - fee)`。把 fee 放在卖出侧，避免同一天买了又卖还倒贴手续费。

```python
def maxProfit_fee(prices, fee):
    hold, cash = -10**18, 0
    for p in prices:
        hold = max(hold, cash - p)
        cash = max(cash, hold + p - fee)
    return cash
```
