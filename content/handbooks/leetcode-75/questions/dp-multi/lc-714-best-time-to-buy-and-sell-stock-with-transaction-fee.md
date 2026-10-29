---
id: lc-714-best-time-to-buy-and-sell-stock-with-transaction-fee
section: dp-multi
order: 3
level: A
title: LC 714 · 买卖股票的最佳时机含手续费
quick: >-
  每天只记两个状态：`cash` 是当天结束时不持股的最大利润，`hold`
  是持股的最大利润。$cash=\max(cash,\,hold+p-fee)$，$hold=\max(hold,\,cash-p)$。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - DP
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 714. Best Time to Buy and Sell Stock with Transaction Fee
    url: >-
      https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定每日股价 prices 和每笔交易的手续费 fee。可以完成任意多次买卖，但任何时刻最多持有一股，必须先卖出当前股票才能再次买入。一笔交易是一买一卖，手续费每笔只扣一次。求所有完整交易的最大总利润。

### 接口与输出

实现 `maxProfit(prices: List[int], fee: int) -> int`。返回扣除手续费后的最大利润；允许不交易，结果至少为 0。

### 合法输入与约束

`1 <= len(prices) <= 50000`，`1 <= prices[i] < 50000`，`0 <= fee < 50000`。本题不限制交易次数，也没有卖出后的冷冻期。

### 示例

```text
输入：prices = [1,3,2,8,4,9], fee = 2
输出：8
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/description/)。

## 解题思路与参考答案

## 题意

`prices[i]` 是第 $i$ 天股价，`fee` 是每笔交易（一买一卖算一笔）的手续费。可以交易任意多次，但手里最多持有一股，必须卖出后才能再买。求最大利润。$1\le n\le 5\times 10^4$。

## 思路

我用两状态 DP，因为每天结束时手里要么没股票、要么有一股，记作 `cash` 和 `hold`。第 $i$ 天价格为 $p$ 时：

- $cash_i=\max(cash_{i-1},\ hold_{i-1}+p-fee)$：今天什么都不做，或者今天卖掉并付手续费。
- $hold_i=\max(hold_{i-1},\ cash_{i-1}-p)$：继续拿着，或者今天用手上的现金买入。

初值 $cash=0$，$hold=-prices[0]$，答案是最后的 `cash`。手续费放在卖出时扣，放在买入时扣也行，只要只扣一次。

拿 `[1,3,2,8,4,9]`、`fee = 2` 来看：第一天 1 块买入，中间涨到 3 再回落到 2，这点涨幅扣完手续费不值得卖；拿到 8 再卖，赚 $8-1-2=5$。之后 4 块买、9 块卖，再赚 $9-4-2=3$，一共 8。

两行可以原地更新：先算新 `cash`，再用它算 `hold`，等于允许同一天卖了又买，这只会多付一次手续费，得不到比正确答案更大的利润，所以结果不变。

不带手续费的 LC 122 可以把每一段上涨都吃掉。这里有手续费，小涨幅不值得交易，贪心得额外处理「延迟卖出」，两状态 DP 更直接。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxProfit([1, 3, 2, 8, 4, 9], 2) == 8
assert maxProfit([1, 3, 7, 5, 10, 3], 3) == 6
assert maxProfit([5], 1) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

只有一天时没法卖，利润是 $0$。

一路下跌时 `cash` 一直是 $0$，不交易。

涨幅小于等于手续费时，交易就会亏，`cash` 不会被更新。

`fee = 0` 时退化成 LC 122，答案是所有正差分之和。

## 追问

**换成冷冻期，卖出后隔一天才能买呢（LC 309）？**
买入时不能用昨天的 `cash`，要用前天的。多存一个 `prev_cash`，$hold_i=\max(hold_{i-1},\ cash_{i-2}-p)$。

```python
def maxProfitCooldown(prices):
    cash, prev_cash, hold = 0, 0, float("-inf")
    for p in prices:
        new_cash = max(cash, hold + p)
        hold = max(hold, prev_cash - p)
        prev_cash, cash = cash, new_cash
    return cash
```

**能用贪心写吗？**
能。维护一个「有效买入价」`buy = prices[0] + fee`。遇到更低的 $p+fee$ 就换买入价；遇到 $p \gt buy$，先把 $p - buy$ 记进利润，再把 `buy` 设成 $p$，意思是之后如果更高还可以接着持有，不用再付一次手续费。时间 $O(n)$，和 DP 等价，但正确性要多解释一步。

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
