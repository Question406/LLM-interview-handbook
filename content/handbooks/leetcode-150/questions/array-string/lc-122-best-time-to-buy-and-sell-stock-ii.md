---
id: lc-122-best-time-to-buy-and-sell-stock-ii
section: array-string
order: 8
level: S
title: LC 122 · 买卖股票的最佳时机 II
quick: >-
  可多次买卖，不能同时持有。所有上升段 `prices[i]-prices[i-1]` 为正就加进去。时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Array
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 122. 买卖股票的最佳时机 II
    url: https://leetcode.cn/problems/best-time-to-buy-and-sell-stock-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`prices[i]` 为第 $i$ 天股价。可以多次买卖，同一天不能同时持有多只，求最大利润。

## 思路

能交易任意次时，最优就是吃掉每一段上涨。相邻差值为正就累加：等价于在每个谷买入、下一个峰卖出。不必真的找峰谷，一步差值即可。

和 LC 121 对比：那里只能吃「全局最大的一段」；这里把所有正增量都拿走。

## 参考代码

```python
from typing import List


def maxProfit(prices: List[int]) -> int:
    ans = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            ans += prices[i] - prices[i - 1]
    return ans


if __name__ == "__main__":
    assert maxProfit([7, 1, 5, 3, 6, 4]) == 7
    assert maxProfit([1, 2, 3, 4, 5]) == 4
    assert maxProfit([7, 6, 4, 3, 1]) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 单调升：相当于首买尾卖，差值之和等于 `prices[-1] - prices[0]`。
- 单调降：全部差值 $\le 0$，利润 $0$。
- 有平价日：差值为 $0$，不加即可，不要特判。

## 追问

- **同一天先卖再买允许吗？** 允许。题面只禁止同时持有两股，卖出后再立刻买入不算同时持有。贪心按相邻正差值累加，数学上等价于「今天卖、今天再买接着拿下一段上涨」，结果与真的在谷峰交易相同。不要为了「同一天不能既买又卖」去合并相邻上涨段——合并后利润不变，写起来更烦。时间仍 $O(n)$。

- **有手续费（LC 714）？** 无限次但每完成一笔扣 `fee`。不能再无脑加正差值：长度为 $1$ 的上涨可能覆盖不了手续费。状态机：`hold` 为持有时的最大收益，`cash` 为空仓。每天 `hold = max(hold, cash - p)`，`cash = max(cash, hold + p - fee)`。手续费只在卖出扣一次，不要买卖各扣。时间 $O(n)$，额外空间 $O(1)$。次数限制见 `lc-188-best-time-to-buy-and-sell-stock-iv`。

```python
def maxProfit_fee(prices, fee):
    hold, cash = float("-inf"), 0
    for p in prices:
        hold, cash = max(hold, cash - p), max(cash, hold + p - fee)
    return cash
```

