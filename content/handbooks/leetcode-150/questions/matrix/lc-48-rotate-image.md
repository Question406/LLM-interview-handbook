---
id: lc-48-rotate-image
section: matrix
order: 3
level: S
title: LC 48 · 旋转图像
quick: >-
  原地顺时针 $90^\circ$：先沿主对角线转置，再左右翻转每一行。时间 $O(n^2)$，额外空间
  $O(1)$。
tags:
  - Matrix
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 48. 旋转图像
    url: https://leetcode.cn/problems/rotate-image/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$n\times n$ 矩阵表示图像，原地顺时针旋转 $90^\circ$。

## 思路

位置映射 $(i,j)\to(j,n-1-i)$。拆成两步更稳：先转置（$(i,j)\leftrightarrow(j,i)$），再把每一行反转，等价于列对称翻转。只交换上三角，避免转置做两次。

按圈四元交换也可以，下标容易写错。面试先画 $2\times 2$ 再写转置 + 翻转。

## 参考代码

```python
from typing import List


def rotate(matrix: List[List[int]]) -> None:
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    for row in matrix:
        row.reverse()


if __name__ == "__main__":
    a = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    rotate(a)
    assert a == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    b = [[1, 2], [3, 4]]
    rotate(b)
    assert b == [[3, 1], [4, 2]]
    print("ok")
```

## 复杂度

时间 $O(n^2)$，额外空间 $O(1)$。

## 边界

- $n=1$：不用动。
- 偶数边长：每个元素都在某个四元环里，转置 + 翻转覆盖全部。
- 奇数边长：中心元素映射到自己，两步交换都碰不到它。

## 追问

- **逆时针 $90^\circ$？** 映射 $(i,j)\to(n-1-j,i)$。实现：先转置，再上下翻转（`matrix.reverse()`）；或先左右翻转再转置。时间仍 $O(n^2)$，额外空间 $O(1)$。

```python
def rotateCCW(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    matrix.reverse()
```

- **$180^\circ$？** 映射 $(i,j)\leftrightarrow(n-1-i,n-1-j)$。实现：每行反转，再整体上下翻转。或连续两次顺时针 $90^\circ$。

```python
def rotate180(matrix):
    for row in matrix:
        row.reverse()
    matrix.reverse()
```
