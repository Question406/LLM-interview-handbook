---
id: lc-162-find-peak-element
section: binary-search
order: 3
level: S
title: LC 162 · 寻找峰值
quick: >-
  峰值：比左右邻居大，两端外视为 $-\infty$。比较 `mid` 与 `mid+1`，往更大的一侧走，那边必有峰。时间
  $O(\log n)$，额外空间 $O(1)$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 162. Find Peak Element
    url: https://leetcode.com/problems/find-peak-element/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

`nums[i]` 是峰值当它严格大于左右邻居。数组两端外侧看成负无穷，相邻元素保证不同。返回任一峰值下标，要求 $O(\log n)$。

## 思路

`nums[mid]` 小于 `nums[mid+1]` 说明右侧在上升：要么一直升到尽头（尽头是峰），要么中途下降（下降前是峰），所以往右收，`lo = mid + 1`。反之往左收，`mid` 自己可能就是峰，所以 `hi = mid`。

区间 $[lo, hi]$ 始终满足「里面一定有峰」，收缩到一个点就是答案。相邻元素保证不同，不会卡在平台。线性扫找第一个下降点也能做，但是 $O(n)$，不符合要求。

## 参考代码

```python
from typing import List


def findPeakElement(nums: List[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo


def isPeak(nums: List[int], i: int) -> bool:
    left = nums[i - 1] if i > 0 else float("-inf")
    right = nums[i + 1] if i + 1 < len(nums) else float("-inf")
    return nums[i] > left and nums[i] > right


if __name__ == "__main__":
    assert findPeakElement([1, 2, 3, 1]) == 2
    assert findPeakElement([1, 2, 1, 3, 5, 6, 4]) in (1, 5)
    assert findPeakElement([1]) == 0
    assert findPeakElement([1, 2, 3, 4]) == 3
    assert findPeakElement([4, 3, 2, 1]) == 0
    for nums in ([3, 1, 2], [1, 3, 2, 4, 1], [2, 1]):
        assert isPeak(nums, findPeakElement(nums))
    print("ok")
```

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## 边界

- $n=1$：两端外侧是 $-\infty$，唯一元素就是峰，循环不进返回 $0$。
- 单调升：每次都往右收，`lo` 推到末尾，峰在最后一个。
- 单调降：每次往左收，`hi = mid` 收到下标 $0$。
- 多个峰：算法保证停在某一个，不必是全局最大。

## 追问

- **二维峰值（LC 1901）？** $m\times n$ 矩阵，峰定义为严格大于四邻（边上缺的方向视为 $-\infty$）。对列二分：取中列 `mid`，找到该列最大值所在行 `row`。若它比左右邻都大，就是峰（上下邻不会更大，因为它是列最大）；左邻更大则峰必在左半，右邻更大则去右半。时间 $O(m\log n)$。

```python
def findPeakGrid(mat):
    m, n = len(mat), len(mat[0])
    lo, hi = 0, n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        row = max(range(m), key=lambda r: mat[r][mid])
        left = mat[row][mid - 1] if mid else float("-inf")
        right = mat[row][mid + 1] if mid + 1 < n else float("-inf")
        if mat[row][mid] > left and mat[row][mid] > right:
            return [row, mid]
        if left > mat[row][mid]:
            hi = mid - 1
        else:
            lo = mid + 1
```

- **为什么比 `mid+1` 而不是 `mid-1`？** 循环条件 `lo < hi` 且 `mid` 向下取整，`mid+1` 一定不越界；比 `mid-1` 要改成向上取整，否则 `mid = lo` 时越界或死循环。
- **允许相邻相等还能 $O(\log n)$ 吗？** 不能保证。全相等数组里没有严格峰，而像 `[1,1,1,2,1,1,1]` 这样的输入，二分看到的中点和邻居都相等，无法判断峰在哪一侧，最坏只能线性扫。
