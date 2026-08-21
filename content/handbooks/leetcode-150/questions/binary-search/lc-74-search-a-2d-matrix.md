---
id: lc-74-search-a-2d-matrix
section: binary-search
order: 2
level: A
title: LC 74 · 搜索二维矩阵
quick: >-
  每行有序，且下一行首大于上一行尾，整表是一维有序。下标 `mid` 映射成
  `(mid // n, mid % n)` 二分。时间 $O(\log(mn))$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 74. 搜索二维矩阵
    url: https://leetcode.cn/problems/search-a-2d-matrix/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$m\times n$ 矩阵：每行从左到右升序，每行第一个数大于上一行最后一个。判断 `target` 是否存在。

## 思路

整表可以看成长度为 $mn$ 的有序数组。对 $[0, mn)$ 二分，`mid` 对应 `matrix[mid // n][mid % n]`。

也可以先按行首二分定位行，再在该行二分，两次 $\log$。第一种更干净。不要和 LC 240 搞混：那题只保证行、列各自有序，不能压成一维。

## 参考代码

```python
from typing import List


def searchMatrix(matrix: List[List[int]], target: int) -> bool:
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = matrix[mid // n][mid % n]
        if v == target:
            return True
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


if __name__ == "__main__":
    grid = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
    assert searchMatrix(grid, 3) is True
    assert searchMatrix(grid, 13) is False
    assert searchMatrix([[1]], 1) is True
    print("ok")
```

## 复杂度

时间 $O(\log(mn))$，额外空间 $O(1)$。

## 边界

- $1\times 1$：`lo == hi == 0`，一次比较即可。
- `target` 小于左上 / 大于右下：第一次 `mid` 就往对应方向出界，返回 `False`。
- 恰在行缝两侧：例如上一行尾 $7$、下一行首 $10$，压成一维后仍相邻有序，二分不会跨行出错。

## 追问

- **LC 240（行、列各自有序，行首不必大于上一行尾）？** 不能再压成一维。从右上角 $(0, n-1)$ 走阶梯：当前值等于 `target` 则命中；当前值更大则整列下方都更大、只能左移；当前值更小则整行左侧都更小、只能下移。每次丢掉一行或一列，时间 $O(m+n)$，额外空间 $O(1)$。左下角对称。不要对每行单独二分再 $O(m\log n)$——能过但不是目标写法。独立卡见 `lc-240`。

```python
def searchMatrixII(matrix, target):
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    i, j = 0, n - 1
    while i < m and j >= 0:
        if matrix[i][j] == target:
            return True
        if matrix[i][j] > target:
            j -= 1
        else:
            i += 1
    return False
```

- **空矩阵 / 空行？** 先判 `not matrix or not matrix[0]`，否则 `n = len(matrix[0])` 会越界。本题约束通常 $m,n \ge 1$，面试仍要开口提一句。空表直接 `False`。

```python
def searchMatrixSafe(matrix, target):
    if not matrix or not matrix[0]:
        return False
    m, n = len(matrix), len(matrix[0])
    lo, hi = 0, m * n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = matrix[mid // n][mid % n]
        if v == target:
            return True
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False
```

