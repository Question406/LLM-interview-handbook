---
id: lc-123-best-time-to-buy-and-sell-stock-iii
section: dp-2d
order: 7
level: A
title: LC 123 · 买卖股票的最佳时机 III
quick: >-
  最多两笔交易。四个状态滚动：第一次买入价、第一次卖出利润、第二次买入的净成本、第二次卖出利润。每天按这个顺序更新，避免同一天买了又卖当两笔。
tags:
  - DP
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 123. 买卖股票的最佳时机 III
    url: https://leetcode.cn/problems/best-time-to-buy-and-sell-stock-iii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

股价数组 `prices`，最多完成两笔买卖（必须先卖再买下一笔）。求最大利润。

## 思路

状态机。维护：

- `buy1`：第一笔买入的最低成本
- `sell1`：只做一笔的最大利润
- `buy2`：第二笔买入后的净成本（现价减去已拿到的 `sell1`）
- `sell2`：两笔做完的最大利润

每天按这个顺序更新，用的是「更新前」的上一状态，不会在同一天把一笔拆成两笔。少做一笔时 `sell2` 仍能继承 `sell1` 的好处（`buy2` 可以很便宜）。

也可以 `dp[k][0/1]` 表示已完成 $k$ 笔、当前是否持股，本题 $k\le 2$。

## 参考代码

```python
from typing import List


def maxProfit(prices: List[int]) -> int:
    buy1 = buy2 = 10**18
    sell1 = sell2 = 0
    for p in prices:
        buy1 = min(buy1, p)
        sell1 = max(sell1, p - buy1)
        buy2 = min(buy2, p - sell1)
        sell2 = max(sell2, p - buy2)
    return sell2


if __name__ == "__main__":
    assert maxProfit([3, 3, 5, 0, 0, 3, 1, 4]) == 6
    assert maxProfit([1, 2, 3, 4, 5]) == 4
    assert maxProfit([7, 6, 4, 3, 1]) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 一路下跌：`sell1`、`sell2` 停在 $0$。
- 最优只做一笔：`buy2` 可以等于「零利润后再买」，`sell2` 会继承 `sell1`，不必特判。
- 两段峰谷分离：四变量按天滚动即可拆开；同一天按 `buy1 → sell1 → buy2 → sell2` 更新，不会把一笔拆成两笔。

## 追问

- **无限次交易（LC 122）？** 限制消失后，每一段上涨都可以单独落袋，等价于把相邻正差全加上。不允许同一天先卖再买时，把连续上涨合成一笔，总和相同。独立卡见 `lc-122-best-time-to-buy-and-sell-stock-ii`。

```python
def maxProfit_unlimited(prices):
    return sum(max(prices[i] - prices[i - 1], 0) for i in range(1, len(prices)))
```

- **最多 $k$ 笔（LC 188）？** 把两对变量扩成 `buy[1..k]`、`sell[1..k]`。对每个价格从 $t=1$ 扫到 $k$：`buy[t] = min(buy[t], p - sell[t-1])`，`sell[t] = max(sell[t], p - buy[t])`。$k \ge n/2$ 时一笔至少占两天，限制不再起作用，退回无限次。独立卡见 `lc-188-best-time-to-buy-and-sell-stock-iv`。

```python
def maxProfit_k(k, prices):
    n = len(prices)
    if n < 2 or k == 0:
        return 0
    if k >= n // 2:
        return sum(max(prices[i] - prices[i - 1], 0) for i in range(1, n))
    buy, sell = [10**18] * (k + 1), [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            buy[t] = min(buy[t], p - sell[t - 1])
            sell[t] = max(sell[t], p - buy[t])
    return sell[k]
```

- **拆成两次「只做一笔」？** 令 `left[i]` 为 `[0..i]` 内一笔最大利润，`right[i]` 为 `[i..n)` 内一笔最大利润，答案是 $\max_i(\textit{left}[i]+\textit{right}[i])$。两次线性扫描，时间 $O(n)$。和四变量状态机等价，可当交叉验证。

```python
def maxProfit_split(prices):
    n = len(prices)
    left, lo = [0] * n, prices[0]
    for i in range(1, n):
        lo = min(lo, prices[i])
        left[i] = max(left[i - 1], prices[i] - lo)
    right, hi = [0] * n, prices[-1]
    for i in range(n - 2, -1, -1):
        hi = max(hi, prices[i])
        right[i] = max(right[i + 1], hi - prices[i])
    return max(left[i] + right[i] for i in range(n))
```
