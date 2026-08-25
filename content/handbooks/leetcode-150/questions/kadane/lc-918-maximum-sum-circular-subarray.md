---
id: lc-918-maximum-sum-circular-subarray
section: kadane
order: 2
level: A
title: LC 918 · 环形子数组的最大和
quick: >-
  答案取普通 Kadane 与 `total` 减最小子数组和的较大者。全负时最小子数组是整个数组，特判直接返回普通最大。时间
  $O(n)$。
tags:
  - Kadane
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 918. 环形子数组的最大和
    url: https://leetcode.cn/problems/maximum-sum-circular-subarray/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

环形数组：首尾相邻。找一段非空连续子数组（可以跨过接缝）使和最大。

## 思路

不跨界：普通最大子数组和。跨界：等价于「总和减去中间被丢掉的那段」，丢掉的应是最小子数组。两边各跑一遍 Kadane。

全负时最小子数组就是整个数组，`total - min` 变成 $0$，对应空段，这题不允许。用「普通最大 $< 0$」判断，直接返回普通最大。

别拆成两段再拼，容易漏边界。

## 参考代码

```python
from typing import List


def maxSubarraySumCircular(nums: List[int]) -> int:
    total = 0
    max_end = min_end = 0
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


if __name__ == "__main__":
    assert maxSubarraySumCircular([1, -2, 3, -2]) == 3
    assert maxSubarraySumCircular([5, -3, 5]) == 10
    assert maxSubarraySumCircular([-3, -2, -3]) == -2
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。一遍同时维护最大、最小结尾和。

## 边界

- 全负：普通最大 $\lt 0$，直接返回最大的那个负数，不能用 `total - min`（那是 $0$）。
- 全正：最小子数组是最小的单个正数，`total - min` $\lt$ `total`，答案是普通 Kadane 即 `total`。
- 只有一个环绕段：例如 `[5, -3, 5]`，丢掉中间 $-3$，`total - min = 10`。

## 追问

- **非环（LC 53）？** 不允许跨接缝，只跑最大结尾和即可：`cur = max(x, cur + x)`，同步维护 `best`。别再算 `total - min`，否则会把「丢掉中间」的跨界段算进来。这题相对线性版多的就是最小子数组和与全负特判。独立卡见 `lc-53-maximum-subarray`。

```python
def maxSubArray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
```

- **长度限制为至多 $k$？** Kadane 不限长度。限长后改成前缀和：最大子段和 $=$ $\max_{1 \le j-i \le k}(pre[j]-pre[i])$，对每个右端 $j$ 要窗口 $[j-k, j)$ 内最小的 `pre[i]`。单调队列存下标，队头过期弹出，队尾前缀不更小就弹出，队头就是窗口最小前缀。时间 $O(n)$。环形再限长要把数组拼两倍，并限制窗口不越过 $n$。

```python
from collections import deque

def maxSubarraySumLenAtMostK(nums, k):
    pre, dq, ans = [0], deque([0]), float("-inf")
    for x in nums:
        pre.append(pre[-1] + x)
    for j in range(1, len(pre)):
        while dq and j - dq[0] > k:
            dq.popleft()
        ans = max(ans, pre[j] - pre[dq[0]])
        while dq and pre[dq[-1]] >= pre[j]:
            dq.pop()
        dq.append(j)
    return ans
```
