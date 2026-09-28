---
id: lc-1493-longest-subarray-of-1s-after-deleting-one-element
section: sliding-window
order: 4
level: A
title: LC 1493 · 删掉一个元素以后全为 1 的最长子数组
quick: >-
  等价于找「最多含一个 $0$」的最长窗口，答案是窗口长度减一，因为必须删掉一个元素。全 $1$ 时也要删，答案 $n-1$。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Sliding Window
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1493. Longest Subarray of 1's After Deleting One Element
    url: https://leetcode.com/problems/longest-subarray-of-1s-after-deleting-one-element/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给 $0/1$ 数组 `nums`，必须删除恰好一个元素，返回删除后只含 $1$ 的最长非空子数组长度；不存在就返回 $0$。$1 \le n \le 10^5$。

## 思路

删掉的那一格在结果里消失，所以要找的是原数组中「最多一个 $0$」的最长窗口，长度减一就是答案。窗口里有一个 $0$ 时删它；没有 $0$ 时只能删一个 $1$，同样减一。

这就是 `lc-1004-max-consecutive-ones-iii` 取 $k = 1$，再在答案上减一。我会直接把 `best` 记成 `right - left`，省掉最后的减法。容易错的是全 $1$ 数组：必须删一个，答案是 $n-1$，不是 $n$。

## 参考代码

```python
from typing import List


def longestSubarray(nums: List[int]) -> int:
    left = zeros = best = 0
    for right, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > 1:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left)
    return best


if __name__ == "__main__":
    assert longestSubarray([1, 1, 0, 1]) == 3
    assert longestSubarray([0, 1, 1, 1, 0, 1, 1, 0, 1]) == 5
    assert longestSubarray([1, 1, 1]) == 2
    assert longestSubarray([0, 0, 0]) == 0
    assert longestSubarray([1]) == 0
    assert longestSubarray([0]) == 0
    assert longestSubarray([1, 0, 0, 1]) == 1
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 全 $1$：必须删一个，答案 $n-1$；长度为 $1$ 时是 $0$。
- 全 $0$：删完剩不出 $1$，答案 $0$。
- 连续两个 $0$ 把数组隔开：两侧的 $1$ 连不起来，只能各算各的。

## 追问

- **不用窗口的写法？** 维护两个计数：`cur` 是当前这段连续 $1$ 的长度，`prev` 是上一个 $0$ 前面那段的长度。遇到 $0$ 时 `prev = cur`、`cur = 0`；每步用 `prev + cur` 更新答案。一个 $0$ 两侧的 $1$ 正好拼在一起。全 $1$ 时答案仍要减一。

```python
def longestSubarrayCounts(nums):
    prev = cur = best = 0
    for x in nums:
        if x == 1:
            cur += 1
        else:
            prev, cur = cur, 0
        best = max(best, prev + cur)
    return best - 1 if best == len(nums) else best
```

- **改成最多删 $k$ 个？** 删的一定是窗口里的 $0$，删完剩下的 $1$ 连成一段，长度是「窗口长度 - 窗口内 $0$ 数」。窗口条件改成 `zeros > k` 时收缩，每步用 `right - left + 1 - zeros` 更新答案。
