---
id: lc-122-best-time-to-buy-and-sell-stock-ii
section: array-string
order: 8
level: S
title: LC 122 · 买卖股票的最佳时机 II
quick: "能多次买卖、但不能同时持有时，最优就是吃掉每一段上涨：相邻差值 `prices[i]-prices[i-1]` 为正就加进去，这和每个谷买、下一个峰卖等价。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Array
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 122. 买卖股票的最佳时机 II
    url: https://leetcode.cn/problems/best-time-to-buy-and-sell-stock-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定整数数组 `prices`，其中 `prices[i]` 是第 i 天一股股票的价格。你可以进行任意多次买卖，但任意时刻最多持有一股股票；一次卖出完成后才可再次买入，也允许同一天先卖后买。开始时没有股票。求所有交易完成后能够获得的最大总利润；也可以不交易。

### 输入与输出

实现 `maxProfit(prices) -> int`。输入为按日期排列的股价列表，返回最大利润的整数值，不需要返回交易日期。

### 约束

- `1 <= len(prices) <= 3 * 10^4`。
- `0 <= prices[i] <= 10^4`。
- 不收取手续费，没有冷冻期，也没有交易次数上限。

### 示例

```text
输入：prices = [7,1,5,3,6,4]
输出：7
```

[LeetCode 原题](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/description/)

## 解题思路与参考答案

## 题意

`prices[i]` 是第 $i$ 天股价。可以多次买卖，同一天不能同时持有多只，求最大利润。

## 思路

能交易任意次，最优就是把每一段上涨都吃掉，所以我只看相邻两天，差值为正就累加。这等价于在每个谷买入、下一个峰卖出，但一步差值就够，不用真去找峰谷。

拿 `[7, 1, 5, 3, 6, 4]` 走一遍：正差值只有 $5-1=4$ 和 $6-3=3$，加起来是 $7$。

和 LC 121 比，那边只能吃全局最大的一段，这里把所有正增量都拿走。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxProfit([7, 1, 5, 3, 6, 4]) == 7
assert maxProfit([1, 2, 3, 4, 5]) == 4
assert maxProfit([7, 6, 4, 3, 1]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

单调上升相当于首日买、末日卖，差值之和正好等于 `prices[-1] - prices[0]`。单调下降时所有差值都 $\le 0$，利润是 $0$。有平价日的话差值为 $0$，不加就行，不用特判。

## 追问

**同一天先卖再买允许吗？**
允许。题面只禁止同时持有两股，卖出后立刻再买不算同时持有。贪心按相邻正差值累加，数学上等价于「今天卖、今天再买，接着拿下一段上涨」，结果和真在谷峰交易一样。没必要为了「同一天不能既买又卖」去合并相邻的上涨段，合并后利润不变，代码更烦。时间仍是 $O(n)$。

**有手续费呢（LC 714）？**
改用状态机。无限次交易但每完成一笔扣 `fee` 时，就不能再无脑加正差值了，长度为 $1$ 的上涨可能覆盖不了手续费。`hold` 是持有时的最大收益，`cash` 是空仓时的最大收益，每天 `hold = max(hold, cash - p)`，`cash = max(cash, hold + p - fee)`。手续费只在卖出时扣一次，别买卖各扣一遍。时间 $O(n)$，额外空间 $O(1)$。有次数限制的版本见 `lc-188-best-time-to-buy-and-sell-stock-iv`。

```python
def maxProfit_fee(prices, fee):
    hold, cash = float("-inf"), 0
    for p in prices:
        hold, cash = max(hold, cash - p), max(cash, hold + p - fee)
    return cash
```
