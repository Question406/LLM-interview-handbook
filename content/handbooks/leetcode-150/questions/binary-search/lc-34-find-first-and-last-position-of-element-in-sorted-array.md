---
id: lc-34-find-first-and-last-position-of-element-in-sorted-array
section: binary-search
order: 5
level: A
title: LC 34 · 在排序数组中查找元素的第一个和最后一个位置
quick: >-
  两次二分：下界是第一个 $\ge$ `target`，上界是第一个 $\gt$ `target`。没有则
  $[-1,-1]$。时间 $O(\log n)$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 34. 在排序数组中查找元素的第一个和最后一个位置
    url: https://leetcode.cn/problems/find-first-and-last-position-of-element-in-sorted-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

非递减数组，返回 `target` 第一次和最后一次出现的下标。不存在返回 $[-1,-1]$。要求 $O(\log n)$。

## 思路

下界：第一个 $\ge target$。若越界或值不是 `target`，没有。上界：第一个 $> target$，最后位置是它减一。

找到一个再左右线性扩，重复很多时退化成 $O(n)$。两次二分写两个函数，比较符只差一个等号。

## 参考代码

```python
from typing import List


def searchRange(nums: List[int], target: int) -> List[int]:
    def bound(upper: bool) -> int:
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < target or (upper and nums[mid] == target):
                lo = mid + 1
            else:
                hi = mid
        return lo

    left = bound(False)
    if left == len(nums) or nums[left] != target:
        return [-1, -1]
    return [left, bound(True) - 1]


if __name__ == "__main__":
    assert searchRange([5, 7, 7, 8, 8, 10], 8) == [3, 4]
    assert searchRange([5, 7, 7, 8, 8, 10], 6) == [-1, -1]
    assert searchRange([], 0) == [-1, -1]
    assert searchRange([1], 1) == [0, 0]
    print("ok")
```

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## 边界

- 空数组：`bound` 返回 $0$，$0 == n$，直接 $[-1,-1]$。
- 只出现一次：下界与上界减一重合。
- 整段都是 `target`：下界 $0$，上界 $n$，答案 $[0, n-1]$。
- `target` 比全部小 / 大：下界分别是 $0$ 但值不匹配，或 $n$，都返回 $[-1,-1]$。

## 追问

- **只数出现次数？** 次数就是「第一个 $\gt$ `target`」减「第一个 $\ge$ `target`」，也就是上界减下界。没有时两者相等（都指向插入位），差为 $0$。不要找到一个再左右线性扩，重复很多时退化 $O(n)$。下界写法与 LC 35 相同。

```python
def count(nums, target):
    def bound(upper):
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < target or (upper and nums[mid] == target):
                lo = mid + 1
            else:
                hi = mid
        return lo
    return bound(True) - bound(False)
```

- **旋转数组里找区间？** 无重复时目标最多一次，退化成 LC 33。有重复时，同一值可能在旋转点被劈成两段：一段在数组头、一段在尾，例如 `[2,2,3,4,2,2]` 里 $2$ 的下标不连续。先用 LC 154 的方式找最小值下标 `p`（相等时 `hi -= 1`），数组拆成有序段 `[0, p)` 与 `[p, n)`，对两段分别做本题的下界/上界。只有一段命中就返回该段 `[L, R]`；两段都有则物理下标不构成单一闭区间，应返回两段（头段与尾段），不能合成「从右段左端到左段右端」（会把中间非 `target` 包进去）。最坏因重复找 `p` 是 $O(n)$。

```python
def searchRangeRotated(nums, target):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        elif nums[mid] < nums[hi]:
            hi = mid
        else:
            hi -= 1
    p = lo

    def bound(l, r, upper):
        while l < r:
            mid = (l + r) // 2
            if nums[mid] < target or (upper and nums[mid] == target):
                l = mid + 1
            else:
                r = mid
        return l

    def seg(l, r):
        a = bound(l, r, False)
        if a == r or nums[a] != target:
            return None
        return [a, bound(l, r, True) - 1]

    left, right = seg(0, p), seg(p, n)
    if left and right:
        return [left, right]
    return left or right or [-1, -1]
```
