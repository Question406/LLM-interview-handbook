---
id: lc-1679-max-number-of-k-sum-pairs
section: two-pointers
order: 4
level: A
title: LC 1679 · K 和数对的最大数目
quick: >-
  排序后左右对撞：和小了 `l` 右移，大了 `r` 左移，等于 `k` 就配一对、两边同时内收。时间 $O(n\log n)$；换成计数哈希可做到
  $O(n)$ 时间、$O(n)$ 空间。
tags:
  - Array
  - Two Pointers
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1679. Max Number of K-Sum Pairs
    url: https://leetcode.com/problems/max-number-of-k-sum-pairs/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

一次操作从 `nums` 里删掉两个和为 `k` 的数。求最多能做多少次操作。每个元素只能用一次。$n \le 10^5$，$1 \le nums[i], k \le 10^9$。

## 思路

排序后 `l`、`r` 从两端出发。和小于 `k`：`nums[l]` 和当前最大的数都凑不够，和谁都配不上，丢掉 `l`。和大于 `k`：`nums[r]` 和最小的数都超了，丢掉 `r`。和等于 `k`：直接配对。交换论证：若最优方案里 `nums[l]` 配了别人，把它换成和 `nums[r]` 配，对数不会变少。

计数哈希更快：扫到 `x` 时若 `cnt[k - x] > 0` 就配一对并减计数，否则 `cnt[x] += 1`。这一节放在双指针下，我先写排序版讲清正确性，再补 $O(n)$ 的哈希版。

## 参考代码

```python
from typing import List


def maxOperations(nums: List[int], k: int) -> int:
    a = sorted(nums)
    l, r = 0, len(a) - 1
    ops = 0
    while l < r:
        s = a[l] + a[r]
        if s == k:
            ops += 1
            l += 1
            r -= 1
        elif s < k:
            l += 1
        else:
            r -= 1
    return ops


if __name__ == "__main__":
    assert maxOperations([1, 2, 3, 4], 5) == 2
    assert maxOperations([3, 1, 3, 4, 3], 6) == 1
    assert maxOperations([2, 2, 2, 2], 4) == 2
    assert maxOperations([1], 2) == 0
    assert maxOperations([5, 5, 5], 10) == 1
    assert maxOperations([1, 1, 1], 5) == 0
    print("ok")
```

## 复杂度

排序版时间 $O(n\log n)$，额外空间 $O(n)$（`sorted` 拷贝；原地排序则为排序栈空间）。

## 边界

- `k` 是偶数且有多个 `k/2`：如 `[3,3,3]`、$k=6$ 只能配一对，指针相遇时停下。
- 所有数都大于等于 `k`：正整数范围下两数之和必然超过 `k`，答案 $0$。
- 只有一个元素：`l == r`，不进循环。

## 追问

- **能做到 $O(n)$ 吗？** 计数哈希一遍扫：先查 `k - x` 有没有剩余，有就配对并减一，否则把 `x` 记进计数。先查后记，同一个元素不会和自己配。时间 $O(n)$，额外空间 $O(n)$。

```python
from collections import Counter


def maxOperations_hash(nums, k):
    cnt = Counter()
    ops = 0
    for x in nums:
        if cnt[k - x] > 0:
            cnt[k - x] -= 1
            ops += 1
        else:
            cnt[x] += 1
    return ops
```
