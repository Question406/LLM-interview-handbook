---
id: lc-54-spiral-matrix
section: matrix
order: 2
level: A
title: LC 54 · 螺旋矩阵
quick: >-
  用 `top`/`bottom`/`left`/`right` four bounds 夹住还没走的区域，按右、下、左、上走一圈，每走完一条边就收紧对应的
  bound。时间 $O(mn)$，额外空间 $O(1)$。
tags:
  - Matrix
  - Simulation
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 54. 螺旋矩阵
    url: 'https://leetcode.cn/problems/spiral-matrix/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一个 m 行 n 列的矩形矩阵，从左上角开始，先向右，随后按顺时针方向依次沿外围、再向内逐圈读取元素，返回访问顺序。每个位置恰好读取一次，不能越过尚未读取区域的 bounds。

### 输入与输出

实现 `spiralOrder(matrix: List[List[int]]) -> List[int]`，输出一个长度为 m*n 的列表，而不是另一个二维矩阵。单行或单列也应按相同含义处理。

### 约束

- `1 <= m,n <= 10`，每行长度相同。
- 矩阵元素在 `[-100,100]`。

### 示例

```text
输入：matrix = [[1,2,3],[4,5,6],[7,8,9]]
输出：[1,2,3,6,9,8,7,4,5]
```

## 解题思路与参考答案

## 题意

$m\times n$ 的矩阵，按顺时针螺旋顺序返回所有元素。

## 思路

我用逐步收紧 bounds 来写，four bounds 夹住还没遍历的区域。先走顶行，然后 `top+=1`；再走右列，`right-=1`；如果还有行，走底行，`bottom-=1`；如果还有列，走左列，`left+=1`。单行或单列时，后两段要用 `top <= bottom`、`left <= right` 挡住，避免重复。

拿 `[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]` 走一遍。第一圈依次是顶行 1、2、3、4，右列 8、12，底行 11、10、9，左列 5。第二圈只剩中间的 6、7，走完这一行后 `top` 已经超过 `bottom`，右列和左列的循环都是空的，底行被 `if` 挡住，最后得到 `1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7`。

方向数组加碰壁转向也可以，白板上我觉得逐步收紧 bounds 更不容易写乱。

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
        1,
        2,
        3,
        4,
        8,
        12,
        11,
        10,
        9,
        5,
        6,
        7,
    ]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert spiralOrder([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]
assert spiralOrder([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]) == [
    1,
    2,
    3,
    4,
    8,
    12,
    11,
    10,
    9,
    5,
    6,
    7,
]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，每个元素访问一次。额外空间 $O(1)$（不计答案）。

## Edge Cases

- $1\times n$ 单行时只走顶边，`top` 超过 `bottom` 之后，后两段被 `if` 挡住，不会回头重复。
- $m\times 1$ 单列时，走完顶边的那一个元素后走右列，也就是这一列剩下的部分，底边和左边被挡住。
- $1\times 1$ 时只输出那一个元素。

## 追问

**生成螺旋矩阵（LC 59）呢？**
开一个 $n\times n$ 的空矩阵，同样维护 four bounds，按右、下、左、上依次填入 $1\ldots n^2$。正方形每圈都完整，但最后一圈可能退化成一行或者一个格，所以还是要用 boundary conditions 挡住。

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

**要逆时针呢？**
从左上角往下出发，边的顺序改成下、右、上、左，单行或单列同样要在后两段加 `if`。也可以先转置再套顺时针。

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
