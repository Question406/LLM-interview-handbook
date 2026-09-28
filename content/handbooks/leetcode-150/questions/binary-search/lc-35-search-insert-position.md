---
id: lc-35-search-insert-position
section: binary-search
order: 1
level: S
title: LC 35 · 搜索插入位置
quick: >-
  有序无重复。二分下界：第一个 $\ge$ `target` 的位置；全小于则返回
  $n$。时间 $O(\log n)$。
tags:
  - Binary Search
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 35. 搜索插入位置
    url: https://leetcode.cn/problems/search-insert-position/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

升序且互异的 `nums`。找到 `target` 的下标；不存在则返回它应插入的位置，使数组仍有序。

## 思路

下界二分。`lo, hi = 0, n`，半开区间。`nums[mid] < target` 时 `lo = mid + 1`，否则 `hi = mid`。结束时 `lo` 就是第一个不小于 `target` 的下标。

写成闭区间也行，但插入位置在尾部时要单独处理 `hi` 出界。区间约定固定一种，不要混。

## 参考代码

```python
from typing import List


def searchInsert(nums: List[int], target: int) -> int:
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


if __name__ == "__main__":
    assert searchInsert([1, 3, 5, 6], 5) == 2
    assert searchInsert([1, 3, 5, 6], 2) == 1
    assert searchInsert([1, 3, 5, 6], 7) == 4
    assert searchInsert([1, 3, 5, 6], 0) == 0
    print("ok")
```

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## 边界

- `target` 小于全部：循环里一直 `hi = mid`，返回 $0$。
- `target` 大于全部：一直 `lo = mid + 1`，返回 $n$，即尾部插入位。
- 恰为第一个 / 最后一个：下界恰好落在该下标，因为第一个 $\ge$ `target` 就是它自己。

## 追问

- **有重复？** 本题声明互异，但同一套下界在非递减数组上仍然正确：返回第一个 $\ge$ `target` 的位置，也就是该值第一次出现处（没有则是应插入处）。若要求插到该值最后一次之后，改用上界。

```python
def searchInsertDup(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

- **上界（第一个 $\gt$ `target`）？** 比较改成 `nums[mid] \le target` 时 `lo = mid + 1`，否则 `hi = mid`。结束时 `lo` 是第一个大于 `target` 的下标；`target` 最后一次出现是 `lo - 1`（需再判是否真的等于）。LC 34 的左右端点就是下界与上界减一。独立卡见 `lc-34-find-first-and-last-position-of-element-in-sorted-array`。

```python
def upper_bound(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```
