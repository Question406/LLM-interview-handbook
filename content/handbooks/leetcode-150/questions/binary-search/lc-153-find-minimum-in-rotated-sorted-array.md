---
id: lc-153-find-minimum-in-rotated-sorted-array
section: binary-search
order: 6
level: A
title: LC 153 · 寻找旋转排序数组中的最小值
quick: >-
  无重复。`nums[mid] > nums[hi]` 则最小值在右半，否则 `mid` 本身或左边。缩到
  `lo == hi`。时间 $O(\log n)$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 153. 寻找旋转排序数组中的最小值
    url: https://leetcode.cn/problems/find-minimum-in-rotated-sorted-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

升序互异数组旋转后，找最小值。要求 $O(\log n)$。

## 思路

最小值是旋转点。和右端比：`nums[mid] > nums[hi]` 说明断点在 `mid` 右侧，`lo = mid + 1`；否则 `mid` 可能就是最小，`hi = mid`。不要和左端比：未旋转时左端一直最小，不好丢弃。

有重复是 LC 154，`nums[mid] == nums[hi]` 时只能 `hi -= 1`。

## 参考代码

```python
from typing import List


def findMin(nums: List[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]


if __name__ == "__main__":
    assert findMin([3, 4, 5, 1, 2]) == 1
    assert findMin([4, 5, 6, 7, 0, 1, 2]) == 0
    assert findMin([11, 13, 15, 17]) == 11
    assert findMin([1]) == 1
    print("ok")
```

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## 边界

- 未旋转（已升序）：`nums[mid]` 一直 $\le$ `nums[hi]`，`hi` 收到 `0`，答案是第一个元素。
- 旋转一次（最小在末尾）：形如 `[2,3,4,5,1]`，`mid` 落在左半时 `nums[mid] \gt nums[hi]`，`lo` 会一路推到末尾。
- $n=1$：`lo == hi`，循环不进，直接返回唯一元素。

## 追问

- **有重复（LC 154）？** 无重复时 `nums[mid] == nums[hi]` 只可能 `mid == hi`。有重复后三元组 `[1,1,1]`、`[3,1,3]`、`[1,3,1]` 无法从一次比较判断断点在哪一侧。`nums[mid] \gt nums[hi]` 仍把 `lo` 推到右半；`nums[mid] \lt nums[hi]` 仍把 `hi` 收到 `mid`；相等时只能 `hi -= 1` 丢掉右端这个确定不是唯一最小值的副本。平均仍很快，全相等时最坏 $O(n)$，无法再保证 $\log$。独立卡见 `lc-154`。

```python
def findMinDup(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        elif nums[mid] < nums[hi]:
            hi = mid
        else:
            hi -= 1
    return nums[lo]
```

- **同时找目标（LC 33）？** 最小值题只跟右端比、丢掉确定更大的半段。要找 `target` 时，先判断 `nums[lo] \le nums[mid]` 哪一半有序，再看 `target` 是否落在该半的值域内，落入则缩进有序半，否则丢这半。一次二分 $O(\log n)$。独立卡见 `lc-33-search-in-rotated-sorted-array`。

```python
def searchRotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```
