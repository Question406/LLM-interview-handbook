---
id: lc-73-set-matrix-zeroes
section: matrix
order: 4
level: A
title: LC 73 · 矩阵置零
quick: >-
  用第一行、第一列当标记。先扫内部，再根据标记置零；`matrix[0][0]`
  行列冲突要单独记。时间 $O(mn)$，额外空间 $O(1)$。
tags:
  - Matrix
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 73. 矩阵置零
    url: https://leetcode.cn/problems/set-matrix-zeroes/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

若 `matrix[i][j]==0`，则把第 $i$ 行和第 $j$ 列全部置 $0$。要求原地，尽量常数额外空间。

## 思路

第一行、第一列既是数据又当标记：内部出现 $0$ 就写 `matrix[i][0]=matrix[0][j]=0`。`(0,0)` 同时代表「第一行有零」和「第一列有零」，必须另用两个布尔量记下原第一行 / 第一列是否本就有零。先处理内部，再回头清第一行、第一列。

开 $O(m+n)$ 数组记行列表最直观。要求 $O(1)$ 时再上标记法。

## 参考代码

```python
from typing import List


def setZeroes(matrix: List[List[int]]) -> None:
    m, n = len(matrix), len(matrix[0])
    first_row = any(matrix[0][j] == 0 for j in range(n))
    first_col = any(matrix[i][0] == 0 for i in range(m))
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = 0
                matrix[0][j] = 0
    for i in range(1, m):
        for j in range(1, n):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
    if first_row:
        for j in range(n):
            matrix[0][j] = 0
    if first_col:
        for i in range(m):
            matrix[i][0] = 0


if __name__ == "__main__":
    a = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
    setZeroes(a)
    assert a == [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
    b = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]
    setZeroes(b)
    assert b == [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间 $O(1)$。

## 边界

- 只有 `(0,0)` 是零：第一行和第一列都要清零，靠两个布尔量同时为真，不能只信 `matrix[0][0]`。
- 第一行有零但第一列没有（或反过来）：只清对应那一条，避免 `(0,0)` 标记串扰。
- 整行 / 整列本来全零：置零后仍全零，标记仍然正确。

## 追问

- **允许 $O(m+n)$？** `row[i]`、`col[j]` 记录该行/列是否出现过零，再扫一遍置零。思路直、不易写错，我会先写这个再压到 $O(1)$。

```python
def setZeroesExtra(matrix):
    m, n = len(matrix), len(matrix[0])
    row = [False] * m
    col = [False] * n
    for i in range(m):
        for j in range(n):
            if matrix[i][j] == 0:
                row[i] = col[j] = True
    for i in range(m):
        for j in range(n):
            if row[i] or col[j]:
                matrix[i][j] = 0
```

- **不能用布尔标记？** 只用第一列当「各行是否清零」的标记，另用一个变量 `col0` 记第一列本身要不要清。先从上到下打标，再从下到上按标记清零，避免提前覆盖第一行里的列标记。

```python
def setZeroesCol0(matrix):
    m, n = len(matrix), len(matrix[0])
    col0 = 1
    for i in range(m):
        if matrix[i][0] == 0:
            col0 = 0
        for j in range(1, n):
            if matrix[i][j] == 0:
                matrix[i][0] = matrix[0][j] = 0
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, 0, -1):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0
        if col0 == 0:
            matrix[i][0] = 0
```
