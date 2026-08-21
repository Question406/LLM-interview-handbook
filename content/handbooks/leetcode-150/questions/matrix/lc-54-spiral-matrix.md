---
id: lc-54-spiral-matrix
section: matrix
order: 2
level: A
title: LC 54 · 螺旋矩阵
quick: >-
  维护 `top`/`bottom`/`left`/`right` 四边界。按右、下、左、上走一圈后收缩对应边。时间
  $O(mn)$，额外空间 $O(1)$。
tags:
  - Matrix
  - Simulation
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 54. 螺旋矩阵
    url: https://leetcode.cn/problems/spiral-matrix/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$m\times n$ 矩阵，按顺时针螺旋顺序返回所有元素。

## 思路

四边界夹住未遍历区域。先走顶行并 `top+=1`，再走右列并 `right-=1`；若仍有行，走底行并 `bottom-=1`；若仍有列，走左列并 `left+=1`。单行或单列时，后两段要用 `top <= bottom`、`left <= right` 挡住，避免重复。

方向数组 + 碰壁转向也可以。面试用边界收缩更不容易写乱。

## 参考代码

```python
from typing import List


def spiralOrder(matrix: List[List[int]]) -> List[int]:
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    ans: List[int] = []
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            ans.append(matrix[top][j])
        top += 1
        for i in range(top, bottom + 1):
            ans.append(matrix[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                ans.append(matrix[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                ans.append(matrix[i][left])
            left += 1
    return ans


if __name__ == "__main__":
    assert spiralOrder([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]
    assert spiralOrder([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [
        1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7
    ]
    print("ok")
```

## 复杂度

时间 $O(mn)$，每个元素访问一次。额外空间 $O(1)$（不计答案）。

## 边界

- $1\times n$ 单行：只走顶边，`top` 超过 `bottom` 后后两段被 `if` 挡住，不会回头重复。
- $m\times 1$ 单列：走完顶的一个元素后走右列（即这一列剩余），底/左被挡住。
- $1\times 1$：只输出那一个。

## 追问

- **生成螺旋矩阵（LC 59）？** $n\times n$ 空矩阵，同样维护四边界，按右、下、左、上依次填入 $1\ldots n^2$。正方形每圈都完整，但最后一圈可能退化成一行或一个格，仍要用边界条件挡住。

```python
def generateMatrix(n):
    mat = [[0] * n for _ in range(n)]
    top, bottom, left, right = 0, n - 1, 0, n - 1
    x = 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            mat[top][j] = x
            x += 1
        top += 1
        for i in range(top, bottom + 1):
            mat[i][right] = x
            x += 1
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                mat[bottom][j] = x
                x += 1
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                mat[i][left] = x
                x += 1
            left += 1
    return mat
```

- **逆时针？** 边的顺序改成下、右、上、左（从左上往下出发）。单行/单列同样要在后两段加 `if`。也可以先转置再套顺时针。

```python
def spiralOrderCCW(matrix):
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    ans = []
    while top <= bottom and left <= right:
        for i in range(top, bottom + 1):
            ans.append(matrix[i][left])
        left += 1
        for j in range(left, right + 1):
            ans.append(matrix[bottom][j])
        bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                ans.append(matrix[i][right])
            right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                ans.append(matrix[top][j])
            top += 1
    return ans
```
