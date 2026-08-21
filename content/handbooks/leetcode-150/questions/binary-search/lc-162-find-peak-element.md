---
id: lc-162-find-peak-element
section: binary-search
order: 3
level: A
title: LC 162 · 寻找峰值
quick: >-
  峰值：比左右邻居大，两端外视为 $-\infty$。比较 `mid` 与 `mid+1`，往更大的一侧走，那边必有峰。时间
  $O(\log n)$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 162. 寻找峰值
    url: https://leetcode.cn/problems/find-peak-element/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`nums[i]` 是峰值当它严格大于邻居。数组两端外侧看成负无穷。返回任一峰值下标，要求 $O(\log n)$。

## 思路

`nums[mid] < nums[mid+1]` 说明右侧在上升：要么一直升到尽头（尽头是峰），要么中途下降（下降前是峰）。往右收。反之往左收，`mid` 自己可能就是峰，所以 `hi = mid`。

相邻元素保证不同，不会卡在平台。线性扫也能做，但不符合时间要求。

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


if __name__ == "__main__":
    assert findPeakElement([1, 2, 3, 1]) == 2
    assert findPeakElement([1, 2, 1, 3, 5, 6, 4]) in (1, 5)
    assert findPeakElement([1]) == 0
    print("ok")
```

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## 边界

- $n=1$：两端外侧是 $-\infty$，唯一元素就是峰，循环不进返回 $0$。
- 单调升：每次 `nums[mid] \lt nums[mid+1]`，`lo` 推到末尾，峰在最后一个。
- 单调降：每次往左收，`hi = mid` 收到下标 $0$。
- 多个峰：算法保证停在某一个，不必是全局最大。

## 追问

- **二维峰值（LC 1901）？** $m\times n$ 矩阵，峰定义为严格大于四邻（边上缺的方向视为 $-\infty$）。对列二分：取中列 `mid`，找到该列最大值所在行 `row`。若它比左邻大、比右邻大，就是峰；左邻更大则峰必在左半（从该列往左是上升，和一维同理），右邻更大则去右半。列方向 $\log n$、每步扫一列 $O(m)$，时间 $O(m\log n)$。对行二分则是 $O(n\log m)$。不要对整表套一维峰值：相邻列之间没有「整列单调」保证。

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

- **允许相邻相等？** 本题保证相邻不同，所以 `mid` 与 `mid+1` 的一次比较就能决定升/降。有平台时 `nums[mid] == nums[mid+1]`，无法判断峰在哪侧。只能沿相等段扩到边界，再看外侧是升还是降：外侧上升就往那侧走，两侧都下降则平台本身是峰。最坏整段相等，退化 $O(n)$，不能再保证 $\log$。

```python
def findPeakWithPlateau(nums):
    n, lo, hi = len(nums), 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        elif nums[mid] > nums[mid + 1]:
            hi = mid
        else:
            r = mid
            while r + 1 < n and nums[r] == nums[r + 1]:
                r += 1
            if r + 1 < n and nums[r] < nums[r + 1]:
                lo = r + 1
            else:
                hi = mid
    return lo
```

