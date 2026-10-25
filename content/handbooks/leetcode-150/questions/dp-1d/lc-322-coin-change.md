---
id: lc-322-coin-change
section: dp-1d
order: 4
level: S
title: LC 322 · 零钱兑换
quick: "完全背包求最小值：$dp[x]$ 表示凑出金额 $x$ 的最少硬币数，枚举最后一枚硬币 $c$，取 $dp[x]=\\min_c(dp[x-c]+1)$。$dp[0]=0$，其余初始化为 $+\\infty$；最后仍无法凑出就返回 $-1$。"
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 322. 零钱兑换
    url: https://leetcode.cn/problems/coin-change/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定硬币面额数组 coins 和非负目标金额 amount。每种面额都可以使用任意多枚，求硬币总面值恰好等于 amount 时，所需硬币的最少数量；不能凑出时返回 -1。

### 接口与输出

实现 `coinChange(coins: List[int], amount: int) -> int`。返回最少枚数，不是不同组合的数量；amount 为 0 时不拿硬币即可完成，返回 0。

### 合法输入与约束

`1 <= len(coins) <= 12`，`1 <= coins[i] <= 2^31-1`，`0 <= amount <= 10000`。每种硬币数量无限，不能把每个面额只使用一次。

### 示例

```text
输入：coins = [1,2,5], amount = 11
输出：3
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/coin-change/description/)。

## 解题思路与参考答案

## 题意

硬币面值是 `coins`，每种无限枚，求凑出金额 `amount` 的最少枚数；凑不出返回 $-1$。

## 思路

这是完全背包求最小值，我会用一维 DP。硬币无限用，凑 $x$ 的最优解拿掉最后一枚硬币 $c$，剩下的一定是凑 $x-c$ 的最优解。

$dp[x]$ 是凑出 $x$ 的最少枚数，$dp[0]=0$。对每个金额 $x$，枚举硬币 $c\le x$，取 $dp[x-c]+1$ 的最小值。拿 `[1, 2, 5]` 凑 $11$ 来说，$dp[11]$ 从 $dp[10]$、$dp[9]$、$dp[6]$ 各加一枚里取最小；$dp[10]=2$（两枚 $5$），所以 $dp[11]=3$。因为硬币无限，金额在外层还是硬币在外层都可以，只要金额是先小后大地算。

初始化时用 `amount+1` 当无穷大，最后还是无穷大就返回 $-1$。按面值从大到小贪心，在非典型币制下是错的，反例放在追问里。

## 参考代码

```python
from typing import List


def coinChange(coins: List[int], amount: int) -> int:
    inf = amount + 1
    dp = [inf] * (amount + 1)
    dp[0] = 0
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x:
                dp[x] = min(dp[x], dp[x - c] + 1)
    return dp[amount] if dp[amount] < inf else -1


if __name__ == "__main__":
    assert coinChange([1, 2, 5], 11) == 3
    assert coinChange([2], 3) == -1
    assert coinChange([1], 0) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert coinChange([1, 2, 5], 11) == 3
assert coinChange([2], 3) == -1
assert coinChange([1], 0) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\mathrm{amount}\cdot |coins|)$，额外空间 $O(\mathrm{amount})$。

## 边界

`amount=0` 不需要硬币，返回 $0$。所有面值都大于金额时，`dp[amount]` 一直是无穷大，返回 $-1$。凑不出的情况（比如 `[2]` 凑 $3$）也一样，不能用贪心硬凑。

## 追问

**改成求方案数（LC 518）呢？**
这是完全背包求组合数，$dp[0]=1$。硬币放外层、金额放内层正向更新，每种组合只计一次；如果金额在外、硬币在内，算出来的是排列数。时间 $O(\mathrm{amount}\cdot |coins|)$。

```python
def change(amount, coins):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for x in range(c, amount + 1):
            dp[x] += dp[x - c]
    return dp[amount]
```

**为什么不能直接贪心？**
因为面值不一定满足贪心需要的条件。`[1,3,4]` 凑 $6$，从大到小贪心得到 $4+1+1$ 三枚，最优是 $3+3$ 两枚。只有「标准币制」这一类才能贪心。白板上先用反例否掉贪心，再写完全背包。

```python
def greedy_wrong(coins, amount):
    coins = sorted(coins, reverse=True)
    cnt = 0
    for c in coins:
        cnt += amount // c
        amount %= c
    return cnt if amount == 0 else -1
# greedy_wrong([1, 3, 4], 6) == 3，而最优是 2
```
