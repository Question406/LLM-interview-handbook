---
id: lc-334-increasing-triplet-subsequence
section: array-string
order: 8
level: S
title: LC 334 · 递增的三元子序列
quick: >-
  维护 `first`（最小的一元结尾）和 `second`（最小的二元递增结尾）。遇到比 `second` 大的数就找到三元组。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 334. Increasing Triplet Subsequence
    url: https://leetcode.com/problems/increasing-triplet-subsequence/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

判断数组中是否存在下标 $i \lt j \lt k$ 使 $nums[i] \lt nums[j] \lt nums[k]$。要求严格递增。长度到 $5\cdot 10^5$，进阶要求时间 $O(n)$、额外空间 $O(1)$。

## 思路

`first` 是目前见过的最小值，`second` 是「前面有个更小数」的数里最小的那个。扫到 `x`：`x <= first` 就更新 `first`；否则 `x <= second` 就更新 `second`；否则 `x > second`，三元组成立。

容易被问的点：`first` 更新到 `second` 后面去了，答案还对吗？对。`second` 被赋值时，它前面一定有一个比它小的数；之后 `first` 换小只影响以后的二元组，已有的 `second` 仍带着那个旧的更小前驱。所以 `x > second` 时一定有合法三元组。

另一种做法是预处理前缀最小值和后缀最大值，找中间某个 $j$ 满足 $\text{premin}[j] \lt nums[j] \lt \text{sufmax}[j]$，时间 $O(n)$ 但空间 $O(n)$。用 `<=` 更新是为了处理相等值，保证严格递增。

## 参考代码

```python
from typing import List


def increasingTriplet(nums: List[int]) -> bool:
    first = second = float("inf")
    for x in nums:
        if x <= first:
            first = x
        elif x <= second:
            second = x
        else:
            return True
    return False


if __name__ == "__main__":
    assert increasingTriplet([1, 2, 3, 4, 5]) is True
    assert increasingTriplet([5, 4, 3, 2, 1]) is False
    assert increasingTriplet([2, 1, 5, 0, 4, 6]) is True
    assert increasingTriplet([20, 100, 10, 12, 5, 13]) is True
    assert increasingTriplet([1, 1, 1, 1]) is False
    assert increasingTriplet([1, 2]) is False
    assert increasingTriplet([1, 1, 2, 2, 3]) is True
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 长度小于 $3$：直接不成立，循环也会返回假。
- 大量相等值：用 `<=` 更新，相等值不会被当成递增。
- `first` 在 `second` 之后被刷小，如 `[2, 5, 1, 6]`：`6 > second=5` 仍正确返回真，对应 `2, 5, 6`。

## 追问

- **要返回三个下标？** `second` 更新时同时记下当时的 `first` 下标，作为这对二元组的前驱。命中时返回「记下的前驱、`second` 下标、当前下标」，不能直接用最新的 `first`，它可能在 `second` 后面。

```python
def increasingTripletIdx(nums):
    first = second = None
    pair_first = None
    for k, x in enumerate(nums):
        if first is None or x <= nums[first]:
            first = k
        elif second is None or x <= nums[second]:
            second = k
            pair_first = first
        else:
            return [pair_first, second, k]
    return []
```

- **推广到长度为 $k$ 的递增子序列？** 这是 LIS 的贪心数组：`tails[t]` 是长度 $t+1$ 的递增子序列的最小结尾，每个数用 `bisect_left` 替换或追加，长度到 $k$ 就返回真。时间 $O(n\log k)$，额外空间 $O(k)$。本题是 $k=3$ 时把数组展开成两个变量。

```python
from bisect import bisect_left


def increasingK(nums, k):
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
            if len(tails) >= k:
                return True
        else:
            tails[i] = x
    return False
```
