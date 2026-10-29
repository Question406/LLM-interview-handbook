---
id: meta-card-triples-exact-selection
section: meta
order: 922
level: A
title: "Meta AI Coding：sum-to-15 card game 的最优 disjoint triples"
quick: "我会先把策略问题缩成能验证的 deterministic 子问题：这手牌最多能组成几组。每次看最小的剩余下标，它要么不用，要么与另外两张组成一组；把这两类情况都比较，就不会遗漏最优解。"
companies:
  - meta
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开报告题型改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：Meta AI Coding：sum-to-15 card game 的最优 disjoint triples"
    url: "https://aceoffer.app/interviews/ai-coding"
    type: secondary
---

## 题目描述

来源：AceOffer 的 Meta AI-enabled 题型综述列出 sum-to-15 card game。以下抽出可精确求解的组合选择模块；牌数限制与“最多互不重叠 triples”目标由手册设定。

### 输入、接口与规则

实现 `max_triples(cards) -> list[tuple[int,int,int]]`。输入为最多 16 张牌的整数值数组，每个值为 1..13；相同值的不同下标视为不同的牌。每个 triple 恰好包含三个不同下标，且对应牌值之和等于 15。返回最多数量的 triples，使每张牌最多出现一次；允许留牌不用。

每个 triple 内的下标升序，返回列表也按 tuple 升序。若最优方案不唯一，返回 lexicographically 最小的列表；没有合法 triple 返回空列表，不修改 cards。这里求一个确定牌组的最优分组，输入不包含未知对手或随机抽牌。请说明为什么优先拿第一个合法 triple 的 greedy 策略可能损失总得分。

### 输入输出示例

```text
cards=[1,5,9,2,6,7] -> [(0,1,2),(3,4,5)]。
cards=[5,5,5,5] -> [(0,1,2)]。
cards=[1,2] -> []。
```

## 回答思路

> **Situation / Task：** 同值牌仍是不同实体；最大化 triples 数量。  
> **Approach / Why：** 用剩余牌的 bitmask 做 memoization，枚举最小剩余下标的所有选择。  
> **Result / Check：** 小牌组穷举对照，并检查输出没有重用下标、每组和为 15。

## 解题思路与参考答案

我会先把策略问题缩成能验证的 deterministic 子问题：这手牌最多能组成几组。每次看最小的剩余下标，它要么不用，要么与另外两张组成一组；把这两类情况都比较，就不会遗漏最优解。

Memoization 以剩余牌 mask 为 key。每个候选方案都先规范排序，再比较组数和 lexicographic order，所以结果可重复，也方便之后拿它做 game strategy 的 oracle。

### 完整参考实现

```python
from functools import lru_cache
from itertools import combinations


def max_triples(cards):
    @lru_cache(None)
    def solve(mask):
        if not mask:
            return ()
        bit = mask & -mask
        i = bit.bit_length() - 1
        rest = mask ^ bit
        best = solve(rest)
        remaining = [j for j in range(i + 1, len(cards)) if rest >> j & 1]
        for j, k in combinations(remaining, 2):
            if cards[i] + cards[j] + cards[k] != 15:
                continue
            candidate = tuple(sorted(((i, j, k),) + solve(rest ^ (1 << j) ^ (1 << k))))
            if len(candidate) > len(best) or (
                len(candidate) == len(best) and candidate < best
            ):
                best = candidate
        return best

    return list(solve((1 << len(cards)) - 1))
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert max_triples([1, 5, 9, 2, 6, 7]) == [(0, 1, 2), (3, 4, 5)]
assert max_triples([5, 5, 5, 5]) == [(0, 1, 2)]
assert max_triples([]) == []
assert max_triples([1, 2]) == []
from random import Random

rng = Random(3)
for _ in range(60):
    cards = [rng.randint(1, 13) for _ in range(8)]
    triples = list(combinations(range(8), 3))
    legal = [t for t in triples if sum(cards[i] for i in t) == 15]
    # Eight cards can contain at most two triples: independently enumerate these.
    candidates = [()] + [(t,) for t in legal]
    candidates += [
        tuple(sorted((a, b))) for a, b in combinations(legal, 2) if not set(a) & set(b)
    ]
    expected = min(candidates, key=lambda c: (-len(c), c))
    assert max_triples(cards) == list(expected)
print('card selection tests passed')
```

## 复杂度与追问

最坏约 `O(2^N*N^2*N)` 时间，其中最后 N 计入方案复制和排序成本；memo 存方案需要约 `O(2^N*N)` 空间。追问完整 game 时需要重新定义状态、对手行为和评分，不能把本模块的最优结果直接当成胜率。
