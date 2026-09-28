---
id: lc-643-maximum-average-subarray-i
section: sliding-window
order: 1
level: S
title: LC 643 · 子数组最大平均数 I
quick: >-
  定长滑窗：先算前 $k$ 个的和，之后每右移一步加进一个、减出一个，维护最大和，最后除以 $k$。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Sliding Window
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 643. Maximum Average Subarray I
    url: https://leetcode.com/problems/maximum-average-subarray-i/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给整数数组 `nums`（长度 $n$）和整数 $k$，找长度恰好为 $k$ 的连续子数组，返回它的最大平均值。误差小于 $10^{-5}$ 即可。$1 \le k \le n \le 10^5$，元素在 $[-10^4, 10^4]$。

## 思路

长度固定，平均值最大等价于和最大，所以全程只比较窗口和，最后除一次 $k$，也少了浮点误差。窗口右移一格时，新和 = 旧和 + `nums[i]` - `nums[i-k]`，一步 $O(1)$。

暴力对每个起点重新求和是 $O(nk)$，$k$ 接近 $n$ 时退化成 $O(n^2)$。`best` 初值要用第一个窗口的和，不能用 $0$：数组可能全负。

## 参考代码

```python
from typing import List


def findMaxAverage(nums: List[int], k: int) -> float:
    s = sum(nums[:k])
    best = s
    for i in range(k, len(nums)):
        s += nums[i] - nums[i - k]
        best = max(best, s)
    return best / k


if __name__ == "__main__":
    assert abs(findMaxAverage([1, 12, -5, -6, 50, 3], 4) - 12.75) < 1e-5
    assert findMaxAverage([5], 1) == 5.0
    assert findMaxAverage([-1, -2, -3], 2) == -1.5
    assert findMaxAverage([0, 4, 0, 3, 2], 1) == 4.0
    assert findMaxAverage([3, 3, 3], 3) == 3.0
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 全负数组：`best` 从第一个窗口起算，初值写 $0$ 会错。
- $k = n$：只有一个窗口，循环不执行，直接返回总和除以 $n$。
- $k = 1$：退化为求最大元素。

## 追问

- **长度至少为 $k$ 的最大平均值（LC 644）？** 窗口不再定长，滑窗失效。我会二分答案 `mid`：把每个数减去 `mid`，问是否存在长度 $\ge k$ 的子数组和 $\ge 0$。用前缀和 `pre[j] - min(pre[0..j-k])` 一遍判定。答案单调，二分到精度 $10^{-5}$，时间 $O(n \log \frac{R}{\epsilon})$。

```python
def findMaxAverageAtLeastK(nums, k):
    lo, hi = min(nums), max(nums)
    while hi - lo > 1e-6:
        mid = (lo + hi) / 2
        pre, prev_min, ok = 0.0, 0.0, False
        pre_k = 0.0
        for i, x in enumerate(nums):
            pre += x - mid
            if i >= k:
                pre_k += nums[i - k] - mid
                prev_min = min(prev_min, pre_k)
            if i >= k - 1 and pre - prev_min >= 0:
                ok = True
                break
        if ok:
            lo = mid
        else:
            hi = mid
    return lo
```

- **要所有窗口的平均值？** 同一个滑窗，每步把 `s / k` 追加进结果即可，时间仍是 $O(n)$。
