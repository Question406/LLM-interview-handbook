---
id: lc-1004-max-consecutive-ones-iii
section: sliding-window
order: 3
level: S
title: LC 1004 · 最大连续1的个数 III
quick: >-
  换个问法：找最长的子数组，里面 $0$ 的个数不超过 $k$。可变滑窗，右端扩张，$0$ 超了就收左端，答案是出现过的最大窗口长度。时间
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
  - title: 1004. Max Consecutive Ones III
    url: https://leetcode.com/problems/max-consecutive-ones-iii/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给 $0/1$ 数组 `nums` 和整数 $k$，最多把 $k$ 个 $0$ 翻成 $1$，返回能得到的最长连续 $1$ 的长度。$1 \le n \le 10^5$，$0 \le k \le n$。

## 思路

翻哪些 $0$ 不用真的去选：一段子数组能翻成全 $1$，当且仅当里面 $0$ 的个数 $\le k$。于是题目变成「$0$ 不超过 $k$ 个的最长子数组」。

右指针每步纳入一个元素，遇 $0$ 计数加一；计数超过 $k$ 就右移左指针，直到把一个 $0$ 移出去。窗口合法性对左端单调：某个左端对当前右端不合法，对更靠右的右端也不合法，所以左指针只进不退，总共 $O(n)$ 步。暴力枚举所有子数组是 $O(n^2)$。

## 参考代码

```python
from typing import List


def longestOnes(nums: List[int], k: int) -> int:
    left = zeros = best = 0
    for right, x in enumerate(nums):
        if x == 0:
            zeros += 1
        while zeros > k:
            if nums[left] == 0:
                zeros -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


if __name__ == "__main__":
    assert longestOnes([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2) == 6
    assert longestOnes([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3) == 10
    assert longestOnes([0, 0], 0) == 0
    assert longestOnes([1, 1], 0) == 2
    assert longestOnes([0, 0, 0], 5) == 3
    print("ok")
```

## 复杂度

时间 $O(n)$，左右指针各走一遍；额外空间 $O(1)$。

## 边界

- $k = 0$：退化成原数组最长连续 $1$。
- $k$ 不小于 $0$ 的总数：整段都能翻，答案 $n$。
- 全 $0$ 且 $k = 0$：窗口一直为空，答案 $0$。

## 追问

- **不收缩的写法？** 窗口只增不减：每步右端进一格，若不合法左端也进一格（用 `if` 代替 `while`）。窗口长度从不变小，最后的 `len - left` 就是历史最大合法长度。代码更短，但要能讲清楚为什么中间窗口可能不合法、答案仍然对。

```python
def longestOnesNoShrink(nums, k):
    left = 0
    for x in nums:
        k -= x == 0
        if k < 0:
            k += nums[left] == 0
            left += 1
    return len(nums) - left
```

- **数据是流、$k$ 很小？** 用长度 $k+1$ 的队列记住最近的 $0$ 的下标。新 $0$ 到来时如果队列已满，左端直接跳到最早那个 $0$ 的下一位，不必逐格移动。
- **只能删一个元素？** 就是 `lc-1493-longest-subarray-of-1s-after-deleting-one-element`：$k = 1$，并且答案要减去删掉的那一格。
