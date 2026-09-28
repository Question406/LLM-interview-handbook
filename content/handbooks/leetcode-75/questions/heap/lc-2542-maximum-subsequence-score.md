---
id: lc-2542-maximum-subsequence-score
section: heap
order: 3
level: A
title: LC 2542 · 最大子序列的分数
quick: >-
  按 `nums2` 从大到小排序，枚举当前元素作为最小值；前面扫过的都不比它小，从中挑 `nums1` 最大的 $k$
  个，用大小为 $k$ 的小根堆维护和。时间 $O(n\log n)$，额外空间 $O(n)$。
tags:
  - Heap
  - Greedy
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2542. Maximum Subsequence Score
    url: https://leetcode.com/problems/maximum-subsequence-score/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

两个长度为 $n$ 的数组 `nums1`、`nums2` 和正整数 $k$。选 $k$ 个下标组成集合 $S$，分数为 $\left(\sum_{i\in S} nums1[i]\right)\cdot \min_{i\in S} nums2[i]$。返回最大分数。$1\le k\le n\le 10^5$，元素非负。

## 思路

分数由两部分相乘，一次优化两个量不好做，我先固定一个：枚举「谁是 `nums2` 的最小值」。把下标按 `nums2` 降序排，扫到第 $i$ 个时，前面扫过的元素 `nums2` 都不小于它。若它是最小值，其余 $k-1$ 个只能从前面挑，为了让和最大就挑 `nums1` 最大的。

用小根堆维护扫过的 `nums1` 里最大的 $k$ 个，以及它们的和 `s`：新元素入堆，超过 $k$ 个就弹出最小的。堆满 $k$ 个时用 `s * nums2[i]` 更新答案。

有个细节：刚入堆的当前元素可能马上被弹出，此时堆里的集合并不包含当前下标，`s * nums2[i]` 用的乘数比这组的真实最小值小。这个值偏低但不会超过某个合法方案，而这组集合在上一步已经用更大的乘数算过，所以不影响最大值。暴力枚举 $\binom{n}{k}$ 种组合显然不行。

## 参考代码

```python
import heapq
import itertools
import random
from typing import List


def maxScore(nums1: List[int], nums2: List[int], k: int) -> int:
    pairs = sorted(zip(nums2, nums1), reverse=True)
    heap: List[int] = []
    s = best = 0
    for b, a in pairs:
        heapq.heappush(heap, a)
        s += a
        if len(heap) > k:
            s -= heapq.heappop(heap)
        if len(heap) == k:
            best = max(best, s * b)
    return best


def brute(nums1: List[int], nums2: List[int], k: int) -> int:
    best = 0
    for idx in itertools.combinations(range(len(nums1)), k):
        best = max(best, sum(nums1[i] for i in idx) * min(nums2[i] for i in idx))
    return best


if __name__ == "__main__":
    assert maxScore([1, 3, 3, 2], [2, 1, 3, 4], 3) == 12
    assert maxScore([4, 2, 3, 1, 1], [7, 5, 10, 9, 6], 1) == 30
    assert maxScore([2, 1, 14, 12], [11, 7, 13, 6], 3) == 168
    assert maxScore([5], [0], 1) == 0
    random.seed(0)
    for _ in range(300):
        n = random.randint(1, 7)
        k = random.randint(1, n)
        a = [random.randint(0, 10) for _ in range(n)]
        b = [random.randint(0, 10) for _ in range(n)]
        assert maxScore(a, b, k) == brute(a, b, k)
    print("ok")
```

## 复杂度

排序 $O(n\log n)$，每个元素入堆出堆各一次 $O(\log k)$，总时间 $O(n\log n)$。额外空间 $O(n)$ 存排序后的数对。

## 边界

- $k=1$：答案是 $\max_i nums1[i]\cdot nums2[i]$，堆每次只留一个，自然覆盖。
- $k=n$：必须全选，答案是 `sum(nums1) * min(nums2)`，只在扫到最后一个时堆满。
- `nums2` 有相同值：排序顺序不影响正确性，相同最小值的元素谁先谁后都会被枚举到。

## 追问

- **为什么按 `nums2` 排而不是按 `nums1`？** 最小值只由一个元素决定，枚举它之后剩下的约束只有「`nums2` 不小于它」，排序后就是一个前缀；而和是可加的，适合用堆维护前 $k$ 大。反过来固定 `nums1` 没有这种前缀结构。
- **同类题？** 「雇佣 $K$ 名工人的最低成本」（LC 857）也是按一个维度排序枚举瓶颈、用堆维护另一个维度的前 $k$ 个。和 `lc-2462-total-cost-to-hire-k-workers` 名字像，但那题是双堆模拟。
