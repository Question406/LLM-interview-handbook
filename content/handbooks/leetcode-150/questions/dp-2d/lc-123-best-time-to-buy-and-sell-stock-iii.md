---
id: lc-123-best-time-to-buy-and-sell-stock-iii
section: dp-2d
order: 7
level: A
title: LC 123 · 买卖股票的最佳时机 III
quick: >-
  最多两笔交易，用四个变量的状态机：第一次买入成本、第一次卖出利润、第二次买入的净成本、第二次卖出利润。每天按这个顺序更新，同一天买了又卖不会被当成两笔，时间
  $O(n)$、空间 $O(1)$。
tags:
  - DP
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 123. 买卖股票的最佳时机 III
    url: 'https://leetcode.cn/problems/best-time-to-buy-and-sell-stock-iii/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

数组 prices[i] 表示某支股票在第 i 天的价格。在这些日期中最多完成两笔交易，使总利润最大。一笔交易包括先买入再卖出；同一时刻最多持有一股，因此必须卖掉已买入的股票后才能开始下一笔。也可以只交易一次或完全不交易。

### 输入与输出

实现 `maxProfit(prices: List[int]) -> int`，返回能够获得的最大总利润。不要求返回交易日期，没有盈利机会时返回 0。

### 约束

- `1 <= len(prices) <= 10^5`，`0 <= prices[i] <= 10^5`。
- 不允许卖空，也不能让两笔持仓区间重叠。

### 示例

```text
输入：prices = [3,3,5,0,0,3,1,4]
输出：6
```

示例可在价格 0 时买入、3 时卖出，再在 1 时买入、4 时卖出，总利润为 6。

## 解题思路与参考答案

## 题意

股价数组 `prices`，最多完成两笔买卖，必须卖掉上一笔才能买下一笔，求最大利润。

## 思路

我会用状态机 DP，四个变量按天滚动。两笔交易把持仓过程切成四个阶段：买了第一笔、卖了第一笔、买了第二笔、卖了第二笔，每个状态只从前一个状态转移过来。

`buy1` 记第一笔买入的最低成本，`sell1` 记只做一笔的最大利润，`buy2` 记第二笔买入后的净成本，也就是现价减去已经拿到的 `sell1`，`sell2` 记两笔做完的最大利润。拿 `[3, 3, 5, 0, 0, 3, 1, 4]` 来说，第一笔在 `0` 买、`3` 卖赚 $3$，第二笔在 `1` 买、`4` 卖再赚 $3$，`sell2` 最后是 $6$。

每天按 `buy1 → sell1 → buy2 → sell2` 的顺序更新，不会在同一天把一笔拆成两笔。少做一笔时 `sell2` 也能继承 `sell1` 的好处，因为 `buy2` 可以很便宜。另一种写法是 `dp[k][0/1]`，表示已完成 $k$ 笔、当前是否持股，本题 $k\le 2$。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxProfit([3, 3, 5, 0, 0, 3, 1, 4]) == 6
assert maxProfit([1, 2, 3, 4, 5]) == 4
assert maxProfit([7, 6, 4, 3, 1]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

一路下跌时 `sell1`、`sell2` 都停在 $0$。最优只做一笔时，`buy2` 可以等于「零利润后再买」，`sell2` 会继承 `sell1`，不用特判。两段峰谷分开时，四个变量按天滚动就能自然拆成两笔。

## 追问

**不限交易次数（LC 122）呢？**
限制没了，每一段上涨都可以单独落袋，等价于把所有相邻正差加起来。不允许同一天先卖再买时，把连续上涨合成一笔，总和一样。独立卡见 `lc-122-best-time-to-buy-and-sell-stock-ii`。

```python
def maxProfit_unlimited(prices):
    return sum(max(prices[i] - prices[i - 1], 0) for i in range(1, len(prices)))
```

**最多 $k$ 笔（LC 188）呢？**
把两对变量扩成 `buy[1..k]`、`sell[1..k]`，对每个价格从 $t=1$ 扫到 $k$：`buy[t] = min(buy[t], p - sell[t-1])`，`sell[t] = max(sell[t], p - buy[t])`。$k \ge n/2$ 时一笔至少占两天，限制不再起作用，退回无限次。独立卡见 `lc-188-best-time-to-buy-and-sell-stock-iv`。

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

**能拆成两次「只做一笔」吗？**
能。令 `left[i]` 为 `[0..i]` 内做一笔的最大利润，`right[i]` 为 `[i..n)` 内做一笔的最大利润，答案是 $\max_i(\textit{left}[i]+\textit{right}[i])$。两次线性扫描，时间 $O(n)$，和四变量状态机等价，可以拿来交叉验证。

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
