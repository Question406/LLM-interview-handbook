---
id: lc-74-search-a-2d-matrix
section: binary-search
order: 2
level: A
title: LC 74 · 搜索二维矩阵
quick: >-
  每行有序，且下一行首大于上一行尾，整张表就是一个一维有序数组。对它二分，下标 `mid` 映射成 `(mid // n, mid % n)`，一次就够。时间
  $O(\log(mn))$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 74. 搜索二维矩阵
    url: 'https://leetcode.cn/problems/search-a-2d-matrix/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定 m 行 n 列的整数矩阵，每一行从左到右非递减，并且每一行的第一个元素严格大于上一行的最后一个元素。判断某个整数是否出现在矩阵中。

### 输入与输出

实现 `searchMatrix(matrix, target) -> bool`。输入是非空矩形二维列表和目标整数，存在则返回 True，否则返回 False。

### 约束与约定

- `1 <= m,n <= 100`。
- 矩阵元素与 target 均在 `[-10000,10000]`。
- 要求时间复杂度为 `O(log(m*n))`。

### 示例

```text
输入：matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
输出：true
```

目标 3 出现在示例矩阵的第一行，因此返回 true。

[官方原题与完整题面](https://leetcode.com/problems/search-a-2d-matrix/description/)。

## 解题思路与参考答案

## 题意

$m\times n$ 矩阵：每行从左到右升序，每行第一个数大于上一行最后一个。判断 `target` 是否存在。

## 思路

我会把整张表当成长度为 $mn$ 的有序数组，直接一次二分。对 $[0, mn)$ 二分时，`mid` 对应 `matrix[mid // n][mid % n]`。

拿题里 $3\times 4$ 的表找 3。`mid=5` 映射到 `(1,1)`，是 11，太大，`hi=4`；`mid=2` 是 `(0,2)` 的 5，还大，`hi=1`；`mid=0` 是 1，太小，`lo=1`；`mid=1` 就是 3，找到。

先按行首二分定位行、再在行内二分也行，是两次 $\log$，压成一维只要一次。别和 LC 240 搞混，那题只保证行、列各自有序，压不成一维。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
grid = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
assert searchMatrix(grid, 3) is True
assert searchMatrix(grid, 13) is False
assert searchMatrix([[1]], 1) is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log(mn))$，额外空间 $O(1)$。

## Edge Cases

$1\times 1$ 时 `lo == hi == 0`，比一次就够。`target` 比左上还小或比右下还大时，`mid` 会一路往对应方向收直到出界，返回 `False`。恰好在行缝两侧的值，比如上一行尾 $7$、下一行首 $10$，压成一维后仍然相邻有序，二分不会跨行出错。

## 追问

**LC 240（行、列各自有序，行首不必大于上一行尾）怎么做？**
从右上角 $(0, n-1)$ 走阶梯，时间 $O(m+n)$，额外空间 $O(1)$，这时表已经压不成一维了。当前值等于 `target` 就命中；当前值更大，整列下方都更大，只能左移；当前值更小，整行左侧都更小，只能下移。每一步丢掉一行或一列。从左下角出发是对称的。每行单独二分是 $O(m\log n)$，能过，但不是面试想要的写法。独立卡见 `lc-240`。

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

**空矩阵或空行呢？**
先判 `not matrix or not matrix[0]`，空表直接返回 `False`，否则 `n = len(matrix[0])` 会越界。本题约束通常是 $m,n \ge 1$，开口时还是提一句。

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
