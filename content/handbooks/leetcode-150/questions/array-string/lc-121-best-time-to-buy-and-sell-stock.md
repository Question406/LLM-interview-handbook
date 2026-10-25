---
id: lc-121-best-time-to-buy-and-sell-stock
section: array-string
order: 7
level: S
title: LC 121 · 买卖股票的最佳时机
quick: "只交易一次，扫一遍就够：维护到当天为止的最低买入价，每天拿当天价减它试卖，更新最大利润。卖出日定了，最优买入就是它之前的最低价。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Array
  - Greedy
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 121. 买卖股票的最佳时机
    url: https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定按日期排列的股票价格，只允许完成至多一笔交易：选择某一天买入一股，再在之后的某一天卖出。求这笔交易能够获得的最大利润。也可以不交易，此时利润为 0。

### 输入与输出

实现 `maxProfit(prices) -> int`。`prices[i]` 表示第 i 天的股价；返回最大利润，不返回买卖日期。卖出日期必须晚于买入日期。

### 约束与约定

- `1 <= len(prices) <= 100000`。
- 每个价格是 `0` 到 `10000` 的整数。

### 示例

```text
输入：prices = [7,1,5,3,6,4]
输出：5
```

示例中可在价格为 1 时买入、价格为 6 时卖出，利润为 5。

[官方原题与完整题面](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/description/)。

## 解题思路与参考答案

## 题意

数组 `prices[i]` 是第 $i$ 天股价。最多买卖一次，先买后卖，求最大利润。做不了交易就返回 $0$。

## 思路

这题只交易一次，我会扫一遍，边走边记历史最低价。卖出日一旦定了，最优的买入日就是它之前的最低价，所以我维护 `min_price`，每天用 `prices[i] - min_price` 试卖一次、更新答案，再把当天价纳入最低价。

拿 `[7, 1, 5, 3, 6, 4]` 走一遍：第二天最低价变成 $1$，之后依次试卖 $5-1=4$、$3-1=2$、$6-1=5$、$4-1=3$，最大是 $5$。

两层循环枚举买卖日没必要。开口我会先说清楚「只交易一次」，和可以多次交易的 LC 122 分开。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxProfit([7, 1, 5, 3, 6, 4]) == 5
assert maxProfit([7, 6, 4, 3, 1]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

单调递减时每天卖都不赚，利润是 $0$。最低价在最后一天时只能买不能卖，还是 $0$。长度为 $1$ 做不完一买一卖，也返回 $0$。

## 追问

**可以多次买卖呢（LC 122）？**
那就吃掉每一段上涨，相邻差值为正就累加。同一时刻还是只能持有一股，但次数不限，这等价于每个谷买、下一个峰卖，只是不必真去找峰谷。121 只能拿全局最大的一段，122 把所有正增量都拿走；平价日差值为 $0$，不加。时间 $O(n)$，额外空间 $O(1)$。独立卡见 `lc-122-best-time-to-buy-and-sell-stock-ii`。

```python
def maxProfit_ii(prices):
    ans = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            ans += prices[i] - prices[i - 1]
    return ans
```

**有冷冻期、手续费，或者最多 $k$ 次呢？**
这几种都走状态机。冷冻期（LC 309）是卖出后必须空仓一天，我维护三个状态：`hold` 是持有，`sold` 是今日卖出，`rest` 是空仓且可以买。每天 `hold = max(hold, rest - p)`，新的 `sold` 是旧 `hold + p`，`rest = max(rest, sold)`，时间 $O(n)$，额外空间 $O(1)$。冷冻期约束的是卖完之后隔一天，买完不用隔。

手续费（LC 714）是无限次交易、每笔卖出扣 `fee`，写成 `cash = max(cash, hold + p - fee)` 就行，时间 $O(n)$。

最多 $k$ 次（LC 188）用 `buy[t]` / `sell[t]` 表示第 $t$ 笔的买入成本和卖出利润，每天对 $t=1..k$ 更新，时间 $O(nk)$，额外空间 $O(k)$。如果 $k \ge n/2$，一笔至少占两天，次数限制就失效了，直接退化为 122。独立卡见 `lc-188-best-time-to-buy-and-sell-stock-iv`。

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
