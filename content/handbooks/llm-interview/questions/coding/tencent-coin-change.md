---
id: tencent-coin-change
section: coding
order: 214
level: A
title: 腾讯 TEG 三面：零钱兑换 I / II 差在哪？
quick: >-
  I 求最少硬币数，`dp[x] = min(dp[x], dp[x-c]+1)`，无解为 inf；II
  求组合数，外层硬币、内层金额，这样不会把排列算进去。先定义状态再写转移，别上来就写递归。
tags:
  - Tencent
  - TEG
  - Coding
  - DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 腾讯混元TEG大模型三面-实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/30d3886e7f4c4a76a5f1a4f3c243dfb4'
    type: candidate-first-hand
---

## 题目描述

完成两种零钱兑换：一种求凑出金额所需的最少硬币数，另一种统计不同的无序硬币组合数。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `coin_change(coins,amount)` 与 `change(amount,coins)`。coins 为互不相同的正整数面额列表，每种可用无限枚；amount 为非负整数。

### 输出与约束

`coin_change`返回最少枚数，无法凑出则返回-1。change 返回组合数量，硬币顺序不同不另计。金额0时最少枚数为0，组合数为1（空组合）；面额列表可为空。

### 示例

```text
coin_change([1,2,5],11) -> 3（5+5+1）
change(5,[1,2,5]) -> 4：5；2+2+1；2+1+1+1；1+1+1+1+1
coin_change([2],3) -> -1，change(3,[2]) -> 0
```

## 解题思路与参考答案

两题都是完全背包，差在求的东西：I（322）求凑出金额所需的最少硬币数，是取最小值；II（518）求凑出金额的组合数，是方案计数。II 的循环顺序决定了数的是组合还是排列，外层硬币、内层金额才是组合。

这是腾讯 TEG / 混元大模型实习三面的题，来自牛客候选人原帖，可信度 A，原话是**“零钱兑换 I 和 II”**，同场还有开放题「对大模型发展的看法」。开放题另外讲产业判断，别在 DP 上超时。

## 思路

I 的 `dp[x]` 是凑出 $x$ 的最少枚数，初值 `dp[0]=0`，其余 $+\infty$，转移是 `dp[x]=\min_c(dp[x-c]+1)`。扫完还是 $\infty$ 就是无解，返回 $-1$。

II 的 `dp[x]` 是凑出 $x$ 的组合数，`dp[0]=1`。必须先枚举硬币再枚举金额，这样每种硬币只按一种顺序进入，数出来的是组合。要是外层金额、内层硬币，`1+2` 和 `2+1` 会被算成两种，就成了排列数。

先写状态和转移，再写循环。直接写不带记忆化的递归会重复计算，写之前要先说清怎么避免。

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

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert coin_change([1, 2, 5], 11) == 3` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 复杂度

两题都是 $O(n\cdot \mathrm{amount})$ 时间、$O(\mathrm{amount})$ 空间。I 的两层循环谁在外面都行；II 外层必须是硬币。

## 追问

**`amount=0` 返回什么？**
I 返回 $0$，II 返回 $1$（空组合）。有硬币但凑不出来时，I 返回 $-1$，II 返回 $0$。

**为什么 II 换了循环顺序就错？**
外层金额会把排列也算进去。当场用 `[1,2]` 凑 $3$ 画个表就能看出来：组合是 $2$，排列是 $3$。

**每种硬币只能用一次呢？**
那就是 01 背包，金额倒序遍历。开放题单独回答，先把 DP implementation 和 base cases 说完。
