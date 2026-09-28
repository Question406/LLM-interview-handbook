---
id: lc-4-median-of-two-sorted-arrays
section: binary-search
order: 7
level: S
title: LC 4 · 寻找两个正序数组的中位数
quick: >-
  在较短数组上二分划分，使左半总数 $(m+n+1)//2$，且
  $\max(A_L,B_L)\le \min(A_R,B_R)$。奇数取左最大，偶数再均右最小。时间 $O(\log(\min(m,n)))$。
tags:
  - Binary Search
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 4. 寻找两个正序数组的中位数
    url: https://leetcode.cn/problems/median-of-two-sorted-arrays/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

两个升序数组 `nums1`、`nums2`，长度 $m,n$。返回合并后的中位数。要求 $O(\log(m+n))$。

## 思路

中位数把全体切成左右两半，左半个数是 $(m+n+1)//2$，且左边最大值不超过右边最小值。只在短数组上枚举切点 $i$，另一数组切点 $j = \mathrm{half}-i$。

$A_L > B_R$ 说明 $i$ 太大，往左收；$B_L > A_R$ 则往右收。切空一侧用 $\pm\infty$ 补。奇数长度中位数就是左半最大；偶数再和右半最小平均。

归并到中点也行，但是 $O(m+n)$，过不了 follow-up 的对数要求。

## 参考代码

```python
from typing import List


def findMedianSortedArrays(nums1: List[int], nums2: List[int]) -> float:
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    lo, hi = 0, m
    half = (m + n + 1) // 2
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        a_left = nums1[i - 1] if i else float("-inf")
        a_right = nums1[i] if i < m else float("inf")
        b_left = nums2[j - 1] if j else float("-inf")
        b_right = nums2[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2.0
        if a_left > b_right:
            hi = i - 1
        else:
            lo = i + 1
    raise ValueError("empty input")


if __name__ == "__main__":
    assert findMedianSortedArrays([1, 3], [2]) == 2.0
    assert findMedianSortedArrays([1, 2], [3, 4]) == 2.5
    assert findMedianSortedArrays([], [1]) == 1.0
    assert findMedianSortedArrays([2], []) == 2.0
    print("ok")
```

## 复杂度

时间 $O(\log(\min(m,n)))$，额外空间 $O(1)$。满足 $O(\log(m+n))$。

## 边界

- 一侧为空：短数组切点只能是 $0$，另一侧切在 `half`，中位数就是非空数组自己的中位数；代码用 $\pm\infty$ 补空侧。
- 总长奇数：左半多一个，答案是 $\max(A_L, B_L)$；偶数再和 $\min(A_R, B_R)$ 平均。
- 短数组切点顶到 $0$ 或 $m$：表示中位数完全由长数组贡献，空侧同样用 $\pm\infty$。

## 追问

- **第 $k$ 小（两有序数组）？** 中位数是第 $(m+n+1)//2$ 小（偶数再和下一个平均）。一般第 $k$ 小（$k$ 从 $1$ 计）：每次比较两数组各自的第 $k//2$ 个，较小那边的前缀不可能含第 $k$ 小，整段丢掉并把 $k$ 减去丢掉的个数。某侧空了直接取另一侧第 $k$ 个。时间 $O(\log(m+n))$。也可用本题划分：左半大小改成 $k$，合法时 $\max(A_L,B_L)$ 就是答案。

```python
def findKth(a, b, k):
    if len(a) > len(b):
        a, b = b, a
    if not a:
        return b[k - 1]
    if k == 1:
        return min(a[0], b[0])
    i = min(len(a), k // 2)
    j = k - i
    if a[i - 1] <= b[j - 1]:
        return findKth(a[i:], b, k - i)
    return findKth(a, b[j:], k - j)


def median_via_kth(a, b):
    n = len(a) + len(b)
    if n % 2:
        return float(findKth(a, b, n // 2 + 1))
    return (findKth(a, b, n // 2) + findKth(a, b, n // 2 + 1)) / 2.0
```

- **未排序？** 先各自 $O(m\log m)$、$O(n\log n)$ 排序再走本题，总时间被排序主导。若只要中位数、允许改原数组：把两分数组合并成一块做快选，期望 $O(m+n)$ 选出第 $k$ 小，最坏 $O((m+n)^2)$。在线、不能改原数组且要严格 $\log$ 时，必须先有序。

```python
import random

def median_unsorted(a, b):
    nums = a + b
    k = (len(nums) - 1) // 2

    def select(lo, hi, kth):
        pivot = nums[random.randint(lo, hi)]
        i, j = lo, hi
        while i <= j:
            while nums[i] < pivot:
                i += 1
            while nums[j] > pivot:
                j -= 1
            if i <= j:
                nums[i], nums[j] = nums[j], nums[i]
                i, j = i + 1, j - 1
        if kth <= j:
            return select(lo, j, kth)
        if kth >= i:
            return select(i, hi, kth)
        return nums[kth]

    n = len(nums)
    if n % 2:
        return float(select(0, n - 1, k))
    return (select(0, n - 1, n // 2 - 1) + select(0, n - 1, n // 2)) / 2.0
```
