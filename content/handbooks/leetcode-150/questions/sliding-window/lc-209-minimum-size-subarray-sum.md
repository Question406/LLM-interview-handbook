---
id: lc-209-minimum-size-subarray-sum
section: sliding-window
order: 1
level: A
title: LC 209 · 长度最小的子数组
quick: >-
  正数数组。右指针扩窗口累加，和 $\ge$ `target` 时左缩并更新最短长度。没有则返回
  $0$。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Sliding Window
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 209. 长度最小的子数组
    url: https://leetcode.cn/problems/minimum-size-subarray-sum/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

正整数数组 `nums` 和 `target`，找最短连续子数组使和 $\ge$ `target`。不存在返回 $0$。

## 思路

元素全正，窗口和随右扩单调增、随左缩单调减，才能滑窗。`right` 一直加；当 `acc >= target` 时，用 `right-left+1` 更新答案，再减掉 `nums[left]` 并左移，直到和不够。

前缀和 + 二分也是 $O(n\log n)$。我会先确认「全是正数」再写滑窗。

## 参考代码

```python
from typing import List


def minSubArrayLen(target: int, nums: List[int]) -> int:
    n = len(nums)
    left = acc = 0
    ans = n + 1
    for right, x in enumerate(nums):
        acc += x
        while acc >= target:
            ans = min(ans, right - left + 1)
            acc -= nums[left]
            left += 1
    return 0 if ans == n + 1 else ans


if __name__ == "__main__":
    assert minSubArrayLen(7, [2, 3, 1, 2, 4, 3]) == 2
    assert minSubArrayLen(4, [1, 4, 4]) == 1
    assert minSubArrayLen(11, [1, 1, 1, 1, 1, 1, 1, 1]) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，每个下标最多进、出窗口一次。额外空间 $O(1)$。

## 边界

- 单个元素就 $\ge$ `target`：第一次进 `while` 长度就是 $1$。
- 整段累加仍不够：`ans` 停在 $n+1$，返回 $0$。
- `target` 恰好等于某段和：左缩到刚好不够之前已经更新过最短长度。

## 追问

- **数组含负数怎么办？** 全正才能「右扩单调增、左缩单调减」，有负数滑窗会漏。改前缀和：`pref[j] - pref[i] \ge target` 且 $j-i$ 最短。单调队列维护「前缀递增」的下标：队头一旦满足差值 $\ge$ `target` 就弹出并更新答案，队尾丢掉不小于当前前缀的旧值。时间 $O(n)$，空间 $O(n)$。这是 LC 862 的模板；找不到返回 $-1$ 还是 $0$ 要跟题面走。别再对每个右端二分乱跳，有负数前缀不单调，普通二分会错。

```python
from collections import deque

def shortestSubarray(nums, target):
    n = len(nums)
    pref = [0] * (n + 1)
    for i, x in enumerate(nums):
        pref[i + 1] = pref[i] + x
    dq = deque()
    ans = n + 1
    for j, p in enumerate(pref):
        while dq and p - pref[dq[0]] >= target:
            ans = min(ans, j - dq.popleft())
        while dq and pref[dq[-1]] >= p:
            dq.pop()
        dq.append(j)
    return 0 if ans == n + 1 else ans
```

- **乘积小于 $k$ 的子数组个数（LC 713）？** 元素同样为正，窗口乘积随右扩变大、左缩变小。`right` 乘上当前数，当 `prod \ge k` 时除以左端并左移。此时以 `right` 结尾、起点在 $[left, right]$ 的子数组乘积都 $\lt k$，答案加上 $right-left+1$。$k \le 1$ 时正整数乘积不可能小于 $k$，直接返回 $0$。时间 $O(n)$，空间 $O(1)$。这块容易栽：用 `+= 1` 只数了最短窗口，漏掉更短左端以外的那些子数组。

```python
def numSubarrayProductLessThanK(nums, k):
    if k <= 1:
        return 0
    prod = 1
    left = ans = 0
    for right, x in enumerate(nums):
        prod *= x
        while prod >= k:
            prod //= nums[left]
            left += 1
        ans += right - left + 1
    return ans
```
