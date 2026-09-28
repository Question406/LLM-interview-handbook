---
id: lc-33-search-in-rotated-sorted-array
section: binary-search
order: 4
level: S
title: LC 33 · 搜索旋转排序数组
quick: >-
  无重复。`mid` 落在有序的那一半里：目标在该半的值域内就缩到这半，否则去另一半。时间
  $O(\log n)$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 33. 搜索旋转排序数组
    url: https://leetcode.cn/problems/search-in-rotated-sorted-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

原本升序的互异数组在 [某下标, 末尾] + [开头, 某下标) 处断开重接。在 $O(\log n)$ 内找 `target`，没有返回 $-1$。

## 思路

旋转后仍有一半有序。`nums[lo] <= nums[mid]` 则左半有序，否则右半有序。目标落在有序半的闭区间内就缩到这半，否则丢这半。

先找最小值再二次二分也行，两次 $\log$；一次二分更常见。有重复是 LC 81，相等时只能 `lo += 1`，最坏 $O(n)$。

## 参考代码

```python
from typing import List


def search(nums: List[int], target: int) -> int:
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


if __name__ == "__main__":
    assert search([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search([1], 0) == -1
    assert search([1], 1) == 0
    print("ok")
```

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## 边界

- 未旋转：`nums[lo] \le nums[mid]` 始终成立，退化成普通有序二分。
- 旋转点在 $1$ 或 $n-1$：有序半几乎是整段，无序半只有一个元素，比较仍正确。
- $n=1$：一次 `mid == target` 判断即可。
- 目标是最小 / 最大：会落到断点两侧的值域判断里，不会因为「不在有序半中间」而漏掉。

## 追问

- **有重复（LC 81）？** 无重复时 `nums[lo] \le nums[mid]` 能唯一判定左半有序。有重复后 `[1,0,1,1,1]` 里 `lo` 与 `mid` 都是 $1$，左半其实无序。相等时无法丢任何一半，只能 `lo += 1`（两端都相等还可同时 `hi -= 1`）。`nums[mid] == target` 已在前面返回，因此丢掉的是非目标副本。全是同一值且不在数组里时，最坏 $O(n)$。返回改成布尔即可。独立卡见 `lc-81`。

```python
def searchDup(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return True
        if nums[lo] == nums[mid]:
            lo += 1
            continue
        if nums[lo] < nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return False
```

- **只找最小值（LC 153）？** 不必判断 `target` 落在哪半。和右端比：`nums[mid] \gt nums[hi]` 则最小值在 `mid` 右侧，`lo = mid + 1`；否则 `mid` 本身可能是最小，`hi = mid`。缩到 `lo == hi`。和左端比不好用：未旋转时左端一直最小，不好丢弃。时间 $O(\log n)$。独立卡见 `lc-153-find-minimum-in-rotated-sorted-array`。

```python
def findMin(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]
```
