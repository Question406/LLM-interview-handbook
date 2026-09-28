---
id: lc-714-best-time-to-buy-and-sell-stock-with-transaction-fee
section: dp-multi
order: 3
level: A
title: LC 714 · 买卖股票的最佳时机含手续费
quick: >-
  两个状态：`cash` 是当天结束时不持股的最大利润，`hold` 是持股的最大利润。$cash=\max(cash,\,hold+p-fee)$，$hold=\max(hold,\,cash-p)$。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - DP
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 714. Best Time to Buy and Sell Stock with Transaction Fee
    url: https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

`prices[i]` 是第 $i$ 天股价，`fee` 是每笔交易（一买一卖算一笔）的手续费。可以交易任意多次，但手里最多持有一股，必须卖出后才能再买。求最大利润。$1\le n\le 5\times 10^4$。

## 思路

每天结束时只有两种状态：不持股 `cash`，持股 `hold`。第 $i$ 天价格为 $p$：

- $cash_i=\max(cash_{i-1},\ hold_{i-1}+p-fee)$：今天什么都不做，或今天卖掉并付手续费。
- $hold_i=\max(hold_{i-1},\ cash_{i-1}-p)$：继续拿着，或今天用手上现金买入。

初值 $cash=0$，$hold=-prices[0]$，答案是最后的 `cash`。手续费放在卖出时扣，放买入时扣也行，但只能扣一次。

两行可以原地更新：先算新 `cash` 再用它算 `hold`，相当于允许同一天卖了再买，这只会多付一次手续费，不会得到比正确答案更大的利润，所以结果不变。不带手续费的 LC 122 可以把每段上涨都吃掉，这里有手续费，小涨幅不值得交易，贪心要额外处理「延迟卖出」，DP 两状态更直接。

## 参考代码

```python
from typing import List


def maxProfit(prices: List[int], fee: int) -> int:
    cash, hold = 0, -prices[0]
    for p in prices[1:]:
        cash = max(cash, hold + p - fee)
        hold = max(hold, cash - p)
    return cash


if __name__ == "__main__":
    assert maxProfit([1, 3, 2, 8, 4, 9], 2) == 8
    assert maxProfit([1, 3, 7, 5, 10, 3], 3) == 6
    assert maxProfit([5], 1) == 0
    assert maxProfit([9, 7, 5, 3], 1) == 0
    assert maxProfit([1, 2, 3, 4, 5], 0) == 4
    assert maxProfit([1, 2], 5) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 只有一天：没法卖，利润 $0$。
- 一路下跌：`cash` 一直是 $0$，不交易。
- 涨幅小于等于手续费：交易反而亏，`cash` 不会更新。
- `fee = 0`：退化成 LC 122，答案是所有正差分之和。

## 追问

- **换成冷冻期（LC 309，卖出后隔一天才能买）？** 买入时不能用昨天的 `cash`，要用前天的。多存一个 `prev_cash`，$hold_i=\max(hold_{i-1},\ cash_{i-2}-p)$。

```python
def maxProfitCooldown(prices):
    cash, prev_cash, hold = 0, 0, float("-inf")
    for p in prices:
        new_cash = max(cash, hold + p)
        hold = max(hold, prev_cash - p)
        prev_cash, cash = cash, new_cash
    return cash
```

- **贪心写法？** 维护「有效买入价」`buy = prices[0] + fee`。遇到更低的 $p+fee$ 就换买入价；遇到 $p \gt buy$ 就先把 $p - buy$ 记入利润，并把 `buy` 设成 $p$，表示如果之后更高还能继续持有而不再付一次手续费。时间 $O(n)$，和 DP 等价，但正确性要多解释一步。

```python
def maxProfitGreedy(prices, fee):
    buy, profit = prices[0] + fee, 0
    for p in prices[1:]:
        if p + fee < buy:
            buy = p + fee
        elif p > buy:
            profit += p - buy
            buy = p
    return profit
```
