---
id: lc-73-set-matrix-zeroes
section: matrix
order: 4
level: A
title: LC 73 · 矩阵置零
quick: >-
  借第一行和第一列当标记位，就能做到 $O(1)$ 额外空间：先扫内部把零记到行首、列首，再按标记置零。`matrix[0][0]`
  同时管着第一行和第一列，所以另用两个布尔量记下它们原本有没有零。时间 $O(mn)$。
tags:
  - Matrix
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 73. 矩阵置零
    url: 'https://leetcode.cn/problems/set-matrix-zeroes/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定整数矩阵 matrix。对于输入矩阵中每一个值为 0 的位置，把它所在的整行和整列都设置为 0，其余位置保留原值。需要依据原始矩阵中的零位置确定受影响的行列，不把新写入的零继续扩散。

### 接口与输出

实现 `setZeroes(matrix: List[List[int]]) -> None`，原地修改矩阵，不返回另一个矩阵。进阶目标是常数额外空间。

### 合法输入与约束

矩阵非空，行数和列数均为 1 到 200，元素为 32 位有符号整数。示例输出是调用后原矩阵的内容。

### 示例

```text
输入：matrix = [[1,1,1],[1,0,1],[1,1,1]]
输出：[[1,0,1],[0,0,0],[1,0,1]]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/set-matrix-zeroes/description/)。

## 解题思路与参考答案

## 题意

若 `matrix[i][j]==0`，则把第 $i$ 行和第 $j$ 列全部置 $0$。要求原地，尽量常数额外空间。

## 思路

我会把第一行和第一列借来当标记位，这样不用另开数组，额外空间是 $O(1)$。内部某格 `matrix[i][j]` 是 $0$，就写 `matrix[i][0]=matrix[0][j]=0`，意思是「第 $i$ 行要清、第 $j$ 列要清」。

麻烦在 `(0,0)` 这一格。它既代表「第一行有零」，又代表「第一列有零」，一格装不下两件事。所以开扫之前，先用两个布尔量记下原来的第一行、第一列本身有没有零。然后先处理内部，最后再回头清第一行、第一列；顺序反过来，标记会被提前抹掉。

拿 `[[1,1,1],[1,0,1],[1,1,1]]` 走一遍。中间的 $0$ 在 `(1,1)`，于是 `matrix[1][0]` 和 `matrix[0][1]` 被写成 $0$。第二遍扫内部时，第 $1$ 行和第 $1$ 列都被清掉。原来的第一行、第一列都没有零，两个布尔量是假，不用再动，结果是 `[[1,0,1],[0,0,0],[1,0,1]]`。

面试时我会先说最直观的做法：开 $O(m+n)$ 的数组记哪些行、列要清。面试官要求 $O(1)$，再换成标记法。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
a = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
setZeroes(a)
assert a == [[1, 0, 1], [0, 0, 0], [1, 0, 1]]
b = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]
setZeroes(b)
assert b == [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，额外空间 $O(1)$。

## Edge Cases

只有 `(0,0)` 是零时，第一行和第一列都要清。这时靠的是两个布尔量同时为真，单看 `matrix[0][0]` 分不出是哪一条。

第一行有零而第一列没有，或者反过来，就只清对应的那一条。两个布尔量分开记，正好避免 `(0,0)` 的标记串扰。

某行或某列本来就全是零也没关系，置零以后还是全零，标记照样正确。

## 追问

**如果允许 $O(m+n)$ 空间呢？**
用 `row[i]`、`col[j]` 记录每行、每列有没有出现过零，再扫一遍置零。思路直、不容易写错，我会先写这个，再压到 $O(1)$。

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

**连两个布尔标记都不能用呢？**
可以只用第一列当「各行要不要清零」的标记，另用一个变量 `col0` 记第一列本身要不要清。先从上到下打标记，再从下到上按标记清零，这样不会提前覆盖第一行里存着的列标记。

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
