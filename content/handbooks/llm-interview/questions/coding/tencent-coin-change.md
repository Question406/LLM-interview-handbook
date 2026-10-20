---
id: tencent-coin-change
section: coding
order: 214
level: A
title: 腾讯 TEG 三面：零钱兑换 I / II 差在哪？
quick: >-
  I 求最少硬币数：`dp[x] = min(dp[x], dp[x-c]+1)`，无解为 inf。II 求组合数：外层硬币、内层金额，避免把排列算进去。先定义状态再写转移，不要上来写递归。
tags:
  - Tencent
  - TEG
  - Coding
  - DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯混元TEG大模型三面-实习面经
    url: https://www.nowcoder.com/feed/main/detail/30d3886e7f4c4a76a5f1a4f3c243dfb4
    type: candidate-first-hand
---

## 真题 / 考点说明

- 公司：腾讯 · TEG / 混元
- 岗位：大模型实习；三面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“零钱兑换 I 和 II”**；同场还有开放题「对大模型发展的看法」

I（322）求凑出金额所需的最少硬币数，是完全背包的最小值问题。II（518）求凑出金额的组合数，是完全背包的方案计数问题。循环顺序决定组合 vs 排列：外层硬币、内层金额才是组合。开放题另说产业判断，不要在 DP 上超时。

## 思路

I：`dp[x]` 凑出 $x$ 的最少枚数，初值 `dp[0]=0`，其余 $+\infty$。`dp[x]=\min_c(dp[x-c]+1)`。扫完仍是 $\infty$ 则无解返回 $-1$。

II：`dp[x]` 凑出 $x$ 的组合数，`dp[0]=1`。必须先枚举硬币再枚举金额，这样每种硬币只按一种顺序进入，数的是组合。若外层金额、内层硬币，会把 `1+2` 和 `2+1` 算成两种，变成排列数。

先写状态和转移，再写循环。直接使用不带记忆化的递归会重复计算，写之前应先说明如何避免。

## 参考代码

```python
from typing import List


def coin_change(coins: List[int], amount: int) -> int:
    inf = amount + 1
    dp = [inf] * (amount + 1)
    dp[0] = 0
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x and dp[x - c] + 1 < dp[x]:
                dp[x] = dp[x - c] + 1
    return dp[amount] if dp[amount] != inf else -1


def change(amount: int, coins: List[int]) -> int:
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for x in range(c, amount + 1):
            dp[x] += dp[x - c]
    return dp[amount]


if __name__ == "__main__":
    assert coin_change([1, 2, 5], 11) == 3
    assert coin_change([2], 3) == -1
    assert coin_change([1], 0) == 0
    assert change(5, [1, 2, 5]) == 4
    assert change(3, [2]) == 0
    assert change(10, [10]) == 1
    print("ok")
```

## 复杂度

两题都是 $O(n\cdot \mathrm{amount})$ 时间、$O(\mathrm{amount})$ 空间。I 的硬币循环内外层都可以；II 外层必须是硬币。

## 边界与追问

1. `amount=0`：I 返回 $0$，II 返回 $1$（空组合）。有硬币但凑不出返回 I 的 $-1$、II 的 $0$。
2. 追问「为什么 II 换循环就错」：外层金额会把排列算进去。当场用 `[1,2]` 凑 $3$ 画表：组合是 $2$，排列是 $3$。
3. 追问每种硬币限用一次：01 背包，金额倒序。开放题单独回答，先完成 DP 的实现和边界说明。
