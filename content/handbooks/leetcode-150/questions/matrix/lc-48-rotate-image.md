---
id: lc-48-rotate-image
section: matrix
order: 3
level: S
title: LC 48 · 旋转图像
quick: "原地顺时针转 $90^\\circ$，先沿主对角线转置，再把每一行左右翻转。时间 $O(n^2)$，额外空间 $O(1)$。"
tags:
  - Matrix
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 48. 旋转图像
    url: https://leetcode.cn/problems/rotate-image/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定 n×n 整数矩阵 `matrix`，把它看作图像，将整张图像顺时针旋转 90 度。原来位于第 r 行、第 c 列的元素，应移动到第 c 行、第 `n-1-r` 列，行列下标均从 0 开始。

### 输入与输出

实现 `rotate(matrix) -> None`，原地更新传入矩阵，不另建一张同样大小的矩阵作为最终结果。示例输出展示调用后的 matrix，函数本身不返回矩阵。

### 约束

- 矩阵必须为正方形，`1 <= n <= 20`。
- `-1000 <= matrix[r][c] <= 1000`。

### 示例

```text
输入：matrix = [[1,2,3],[4,5,6],[7,8,9]]
输出：[[7,4,1],[8,5,2],[9,6,3]]
```

[LeetCode 原题](https://leetcode.com/problems/rotate-image/description/)

## 解题思路与参考答案

## 题意

$n\times n$ 的矩阵表示一张图像，要原地顺时针旋转 $90^\circ$。

## 思路

我把旋转拆成转置加每行反转两步，位置映射是 $(i,j)\to(j,n-1-i)$，直接按这个做四元交换，下标很容易写错。先转置，$(i,j)\leftrightarrow(j,i)$，只交换上三角，免得同一对被换两次又换回来；再把每一行反转，相当于左右镜像。

拿 `[[1, 2, 3], [4, 5, 6], [7, 8, 9]]` 走一遍。转置后是 `[[1, 4, 7], [2, 5, 8], [3, 6, 9]]`，每行反转得到 `[[7, 4, 1], [8, 5, 2], [9, 6, 3]]`，正好是顺时针转了 $90^\circ$。

按圈做四元交换也可以写。白板上我会先画一个 $2\times 2$，再写转置 + 翻转。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
a = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
rotate(a)
assert a == [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
b = [[1, 2], [3, 4]]
rotate(b)
assert b == [[3, 1], [4, 2]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n^2)$，额外空间 $O(1)$。

## 边界

- $n=1$ 时不用动。
- 偶数边长时每个元素都在某个四元环里，转置加翻转覆盖了全部。
- 奇数边长时中心元素映射到自己，两步交换都碰不到它。

## 追问

**逆时针 $90^\circ$ 呢？**
映射是 $(i,j)\to(n-1-j,i)$。先转置，再上下翻转（`matrix.reverse()`）；或者先左右翻转再转置。时间还是 $O(n^2)$，额外空间 $O(1)$。

```python
def rotateCCW(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i + 1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    matrix.reverse()
```

**转 $180^\circ$ 呢？**
映射是 $(i,j)\leftrightarrow(n-1-i,n-1-j)$。每行反转之后再整体上下翻转，或者连续做两次顺时针 $90^\circ$。

```python
def rotate180(matrix):
    for row in matrix:
        row.reverse()
    matrix.reverse()
```
