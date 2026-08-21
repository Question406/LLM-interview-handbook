---
id: lc-121-best-time-to-buy-and-sell-stock
section: array-string
order: 7
level: S
title: LC 121 · 买卖股票的最佳时机
quick: >-
  只交易一次。扫一遍维护历史最低买入价，每天用当天价减它试卖出，更新最大利润。时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Array
  - Greedy
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 121. 买卖股票的最佳时机
    url: https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

数组 `prices[i]` 是第 $i$ 天股价。最多买卖一次（先买后卖），求最大利润。不能交易则返回 $0$。

## 思路

卖出日固定时，最优买入是它之前的最低价。从左扫：维护 `min_price`，每天算 `prices[i] - min_price` 更新答案，再把当天纳入最低价。

不要两层循环枚举买卖日。面试先点明「只交易一次」，再和 LC 122（可多次）区分。

## 参考代码

```python
from typing import List


def maxProfit(prices: List[int]) -> int:
    min_price = prices[0]
    ans = 0
    for p in prices:
        ans = max(ans, p - min_price)
        min_price = min(min_price, p)
    return ans


if __name__ == "__main__":
    assert maxProfit([7, 1, 5, 3, 6, 4]) == 5
    assert maxProfit([7, 6, 4, 3, 1]) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 单调递减：每天卖出都不赚，利润 $0$。
- 最低价在最后一天：只能买不能卖，同样 $0$。
- 长度为 $1$：无法完成一买一卖，返回 $0$。

## 追问

- **可以多次买卖（LC 122）？** 同一时刻仍只能持有一股，但交易次数不限。最优是吃掉每一段上涨：相邻差值为正就累加。等价于每个谷买、下一个峰卖，但不必真找峰谷。时间 $O(n)$，额外空间 $O(1)$。和本题的差别：121 只能拿全局最大的一段，122 把所有正增量都拿走。平价日差值为 $0$，不要加。独立卡见 `lc-122-best-time-to-buy-and-sell-stock-ii`。

```python
def maxProfit_ii(prices):
    ans = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            ans += prices[i] - prices[i - 1]
    return ans
```

- **冷冻期 / 手续费 / 最多 $k$ 次？** 都走状态机。冷冻期（LC 309）：卖出后必须空仓一天。维护 `hold`（持有）、`sold`（今日卖出）、`rest`（空仓且可买）。每天 `hold = max(hold, rest - p)`，新的 `sold` 为旧 `hold + p`，`rest = max(rest, sold)`。时间 $O(n)$，额外空间 $O(1)$。手续费（LC 714）：无限次但每笔卖出扣 `fee`，把 `cash = max(cash, hold + p - fee)` 即可，时间 $O(n)$。最多 $k$ 次（LC 188）：`buy[t]` / `sell[t]` 表示第 $t$ 笔买入成本与卖出利润，每天对 $t=1..k$ 更新；若 $k \ge n/2$，一笔至少占两天，限制失效，退化为 122。时间 $O(nk)$，额外空间 $O(k)$。独立卡见 `lc-188-best-time-to-buy-and-sell-stock-iv`。易错点：冷冻期是「卖完隔一天」而不是「买完隔一天」。

```python
def maxProfit_cooldown(prices):
    hold, sold, rest = float("-inf"), 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)


def maxProfit_fee(prices, fee):
    hold, cash = float("-inf"), 0
    for p in prices:
        hold, cash = max(hold, cash - p), max(cash, hold + p - fee)
    return cash


def maxProfit_k(k, prices):
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
```

