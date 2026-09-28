---
id: lc-53-maximum-subarray
section: kadane
order: 1
level: S
title: LC 53 · 最大子数组和
quick: >-
  Kadane：`dp = max(x, dp + x)`，当前数单开一段还是接上一段。同步维护全局最大。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - DP
  - Kadane
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 53. 最大子数组和
    url: https://leetcode.cn/problems/maximum-subarray/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

整数数组 `nums` 非空，找一段连续子数组，使其和最大，返回这个和。

## 思路

`dp` 表示以当前元素结尾的最大和：前面那段是正的就接上，否则从自己重新开。全局答案取所有 `dp` 的最大，也叫 Kadane。

分治也能做：跨中点的最大和 = 左向最大后缀 + 右向最大前缀，再和左右递归比，时间 $O(n\log n)$，白板当备选。

## 参考代码

```python
from typing import List


def maxSubArray(nums: List[int]) -> int:
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


if __name__ == "__main__":
    assert maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert maxSubArray([1]) == 1
    assert maxSubArray([5, 4, -1, 7, 8]) == 23
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 全负：`cur` 每次都从自己重开，`best` 是最大的那个负数。空子数组和为 $0$ 这题不允许，不能返回 $0$。
- 单元素：循环不进，返回它自己。
- 全正：整段相加就是答案。

## 追问

- **还要下标？** `cur` 从 `x` 重开时记下起点 `s`；`cur` 刷新 `best` 时记下 `[s, i]`。别在 `cur + x == x` 时随便改起点，否则全 $0$ 会把区间拆碎。返回和与闭区间。

```python
def maxSubArrayRange(nums):
    best = cur = nums[0]
    start = end = s = 0
    for i in range(1, len(nums)):
        if cur + nums[i] < nums[i]:
            cur = nums[i]
            s = i
        else:
            cur += nums[i]
        if cur > best:
            best, start, end = cur, s, i
    return best, start, end
```

- **环形数组（LC 918）？** 线性 Kadane 只覆盖不跨界的段。跨界最大和 $=$ 总和 $-$ 最小子数组和（中间丢掉的是「最负」的一段）。两边各跑一遍。全负时最小子数组是整个数组，`total - min` 变成 $0$（空段），这题与 LC 918 都不允许，用「普通最大 $\lt 0$」特判，直接返回普通最大。独立卡见 `lc-918-maximum-sum-circular-subarray`。

```python
def maxSubarraySumCircular(nums):
    total = max_end = min_end = 0
    max_sum = min_sum = nums[0]
    for x in nums:
        total += x
        max_end = max(x, max_end + x)
        min_end = min(x, min_end + x)
        max_sum = max(max_sum, max_end)
        min_sum = min(min_sum, min_end)
    if max_sum < 0:
        return max_sum
    return max(max_sum, total - min_sum)
```
