---
id: lc-188-best-time-to-buy-and-sell-stock-iv
section: dp-2d
order: 8
level: A
title: LC 188 · 买卖股票的最佳时机 IV
quick: "这是 LC 123 的推广：`buy[t]` / `sell[t]` 记第 $t$ 笔买入后的净成本和卖出后的利润，每个价格从 $t=1$ 到 $k$ 更新一遍，时间 $O(nk)$。若 $k\\ge n/2$，限制失效，退化为无限次交易，把所有上涨段加起来。"
tags:
  - DP
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 188. 买卖股票的最佳时机 IV
    url: https://leetcode.cn/problems/best-time-to-buy-and-sell-stock-iv/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定每日股价 prices 和交易次数上限 k。一次交易由买入一股和之后卖出这一股构成；任何时刻最多持有一股，必须先结束当前交易才能再买入。请选择至多 k 次完整交易，使总利润最大。

### 接口与输出

实现 `maxProfit(k: int, prices: List[int]) -> int`。返回最大可实现利润，不要求输出交易日期；也可以选择完全不交易，获得利润 0。

### 合法输入与约束

`1 <= k <= 100`，`1 <= len(prices) <= 1000`，`0 <= prices[i] <= 1000`。本题没有手续费或冷冻期；卖出日不能早于相应的买入日。

### 示例

```text
输入：k = 2, prices = [2,4,1]
输出：2
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/description/)。

## 解题思路与参考答案

## 题意

股价 `prices`，最多完成 $k$ 笔交易，求最大利润。每一笔仍是先买后卖。

## 思路

这是 LC 123 的推广，我会把两对变量扩成长度 $k$ 的数组。`buy[t]`、`sell[t]` 分别是完成第 $t$ 笔买入后的净成本、卖出后的利润，对每个价格从 $t=1..k$ 依次更新：

`buy[t] = min(buy[t], p - sell[t-1])`，`sell[t] = max(sell[t], p - buy[t])`。

拿 $k=2$、`[3, 2, 6, 5, 0, 3]` 来说，第一笔 `2` 买 `6` 卖赚 $4$，第二笔 `0` 买 `3` 卖赚 $3$，`sell[2]` 最后是 $7$。

$k$ 很大时（$k \ge n/2$）限制不起作用，任意上涨都可以单独成交，退化成无限次，直接累加 `max(prices[i]-prices[i-1], 0)`。其余情况 DP 是 $O(nk)$，$k$ 很大时不先做这一步剪枝会超时。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxProfit(2, [2, 4, 1]) == 2
assert maxProfit(2, [3, 2, 6, 5, 0, 3]) == 7
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(nk)$，额外空间 $O(k)$；$k\ge n/2$ 时时间 $O(n)$。

## 边界

$k=0$ 或 $n \lt 2$ 时一笔都做不成，直接返回 $0$。单调下跌时所有 `sell[t]` 停在 $0$。$k=1$ 时只更新一对 `buy/sell`，退化为「最低买入、最高卖出」，也就是 LC 121，独立卡见 `lc-121-best-time-to-buy-and-sell-stock`。

## 追问

**为什么 $k \ge n/2$ 就等于无限次？**
一笔交易至少占一个买日和一个卖日，最多 $\lfloor n/2\rfloor$ 笔能成交，$k$ 再大也挤不进更多交易，限制就失效了。这时把所有相邻正差加起来即可，不用再跑 $O(nk)$。

```python
def maxProfit_unlimited(prices):
    return sum(max(prices[i] - prices[i - 1], 0) for i in range(1, len(prices)))
```

**有冷冻期（LC 309）呢？**
卖出后必须空仓一天才能再买，用三个变量：`hold` 持股，`sold` 今天刚卖，`rest` 已过冷冻期的空仓。`hold` 来自继续持有或 `rest - p`；`sold = hold + p`；`rest` 取「继续空仓」和「昨天刚卖」的较大者。最后返回 `max(sold, rest)`。

```python
def maxProfit_cooldown(prices):
    hold, sold, rest = -10**18, 0, 0
    for p in prices:
        hold, sold, rest = max(hold, rest - p), hold + p, max(rest, sold)
    return max(sold, rest)
```

**有手续费（LC 714）呢？**
交易次数不限，但每笔卖出扣 `fee`。`hold` 是持股时的最大利润，`cash` 是空仓时的。每天 `hold = max(hold, cash - p)`，`cash = max(cash, hold + p - fee)`。fee 放在卖出侧，避免同一天买了又卖还倒贴手续费。

```python
def maxProfit_fee(prices, fee):
    hold, cash = -10**18, 0
    for p in prices:
        hold = max(hold, cash - p)
        cash = max(cash, hold + p - fee)
    return cash
```
