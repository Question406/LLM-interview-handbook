---
id: p3a-xai-distinct-integers-after-offset
section: xai
order: 610
level: A
title: "xAI：数组元素各加 [-k,k] 后最多不同值"
quick: "我会把每个 x 看成可选区间 [x - k, x + k]，排序后尽量分配比 last 大的最小整数，把空间留给后面的元素。分不到新值就保留原值；这个证明只适用于偏移可重复使用的版本，偏移只能用一次时要另建模型。"
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · distinct-integers-after-offset"
    url: https://www.1point3acres.com/interview/problems/company/xai/distinct-integers-after-offset
    type: secondary
---

## 题目描述

数组中每个整数都可以独立向左或向右调整最多 k。求能够得到的最大不同值数量，并返回一个达到最优值的数组。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `distinct(nums, k) -> tuple[int, list[int]]`：返回 (最多能得到的不同值个数, 一个达到该个数的变换后数组)。数组保持原下标，每个位置的新值与原值相差不超过 k。
- $k \ge 0$。
- 不同元素可以使用相同的偏移量。偏移只能用一次的变体不在本练习范围内。
- nums 为长度 n<=100000 的整数数组，k 为非负整数；空数组返回 (0,[])。同一个位置只选择一个最终偏移，不同位置可重复使用偏移，任意最优见证数组均可。

### 输入输出示例

```text
distinct([1, 1, 1], 1) -> (3, [0, 1, 2])
distinct([1, 1, 1], 0) -> (1, [1, 1, 1])
distinct([], 2)        -> (0, [])
```

## 解题思路与参考答案

普通版本可以排序后贪心：每个元素都取比上次分配值更大的最小可行整数。例如 `[1, 1, 1]` 在 k 为 1 时能依次变成 `[0, 1, 2]`。这里允许多个元素用同一个偏移量，偏移不可重复的版本需要另行处理。

## 题目

给一个整数数组和非负整数 k。每个元素可以独立地加上 $[-k, k]$ 内的任意整数，问变换后数组最多能有多少个不同的值。题卡还提到一个少见的变体：每个偏移量只能用一次。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题，只覆盖偏移可以重复使用的普通版本。

## 思路

把每个元素 x 看成一个可选区间 $[x - k, x + k]$，问题变成：给尽量多的区间各分配一个互不相同的整数。

贪心做法：按 x 排序，依次处理每个区间，分配「比上一个分配值大的最小可行整数」，也就是 `max(x - k, last + 1)`。如果这个值超出了右端点 $x + k$，这个元素就分不到新值，保留原值即可。

取最小可行值，是为了给后面的区间留下尽可能多的空间。所有区间等长，所以按 x 排序后，左右端点都单调不减；当前少占一点，不会妨碍后续区间的选择。

偏移不可重复的变体多了一个跨元素的全局约束，上面的贪心证明不再成立，需要单独建模，不要直接套用。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `distinct(nums, k) -> tuple[int, list[int]]`：返回 (最多能得到的不同值个数, 一个达到该个数的变换后数组)。数组保持原下标，每个位置的新值与原值相差不超过 k。
- $k \ge 0$，否则抛 `ValueError`；$n \le 10^5$。
- 不同元素可以使用相同的偏移量。偏移只能用一次的变体不在本练习范围内。

### 输入输出示例

```text
distinct([1, 1, 1], 1) -> (3, [0, 1, 2])
distinct([1, 1, 1], 0) -> (1, [1, 1, 1])
distinct([], 2)        -> (0, [])
```

### 解题思路与正确性

证明时可以从一个最优方案出发：它给当前区间分配 v，而贪心给的是更小的 c。c 比之前所有分配值都大，所以此前没有被占用。如果最优方案里后面某个区间用了 c，就把两者交换：那个区间包含 c，而 c < v，它的右端点又不小于当前区间的右端点（也就不小于 v），所以它也能用 v。如果没人用 c，直接把 v 换成 c。所以贪心的选择不会让最优值变小。

分不到新值的元素保留原值，不会多出一个不同值。原因是分配值严格递增，而且只有当某个区间的左端点超过 `last + 1` 时才会出现空档；左端点单调不减，所以所有空档都在当前区间的左端点之下。分配失败时 `last` 已经不小于 $x + k$，区间 $[x - k, x + k]$ 里的每个整数都已被占用，原值 x 也在其中。测试用暴力枚举验证了返回数组的不同值个数确实等于最优值。

### 完整参考实现（Python 3）

```python
import itertools


def distinct(nums, k):
    """每个元素可以加上 [-k, k] 内的任意整数，返回 (最多能有几个不同值, 一种变换后的数组)。"""
    if k < 0:
        raise ValueError(f"k must be >= 0, got {k}")

    result = list(nums)
    last_used = None  # 目前分配出去的最大值；分配值严格递增
    count = 0
    # 所有区间 [x - k, x + k] 等长，按 x 排序就同时按左、右端点排好了
    for value, index in sorted((value, index) for index, value in enumerate(nums)):
        low, high = value - k, value + k
        choice = low if last_used is None else max(low, last_used + 1)
        if choice <= high:
            result[index] = choice
            last_used = choice
            count += 1
        # 分不到新值的元素保留原值：此时 [low, last_used] 已经全部被占用，
        # 原值必然和某个已分配值重复，不会多出一个不同值
    return count, result
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert distinct([1, 1, 1], 1) == (3, [0, 1, 2])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def brute_force(nums, k):
    choices = (range(x - k, x + k + 1) for x in nums)
    return max(len(set(candidate)) for candidate in itertools.product(*choices))

# 三个相同元素，k = 1 时可以拉开成 0, 1, 2
assert distinct([1, 1, 1], 1) == (3, [0, 1, 2])

# k = 0 时不能改动
assert distinct([1, 1, 1], 0)[0] == 1

# 和暴力枚举对照：返回的数组也必须真的有这么多不同值
for nums in itertools.product(range(3), repeat=3):
    count, result = distinct(nums, 1)
    best = brute_force(nums, 1)
    assert count == best
    assert len(set(result)) == best
    assert all(abs(new - old) <= 1 for new, old in zip(result, nums))

# 空数组
assert distinct([], 2) == (0, [])
```

### 复杂度与追问

设数组长度为 n。排序 O(n log n)，扫描 O(n)，额外空间 O(n)。

如果每个偏移量只能用一次，元素之间的选择互相耦合：一个元素用了 +1，别的元素就不能再用 +1。这时既要偏移量互不相同，又要结果值尽量不同，问题结构已经和普通版本不一样，不能沿用这里的证明或实现。动手前先和面试官确认规模，小规模可以先写搜索或暴力作为基准。
