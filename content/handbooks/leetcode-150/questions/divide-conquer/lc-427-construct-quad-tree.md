---
id: lc-427-construct-quad-tree
section: divide-conquer
order: 3
level: A
title: LC 427 · 建立四叉树
quick: >-
  $n\times n$ 网格四分。四块全同则合成叶 `Node(val, True)`，否则
  `Node(val, False, topLeft, topRight, bottomLeft, bottomRight)`。时间 $O(n^2)$。
tags:
  - Divide and Conquer
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 427. 建立四叉树
    url: https://leetcode.cn/problems/construct-quad-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$n\times n$ 的 $0/1$ 网格（$n$ 为 $2$ 的幂）建成四叉树。一块全相同则为叶，`val` 表示该块取值；否则四个孩子依次是左上、右上、左下、右下。

## 思路

对当前正方形递归。边长为 $1$ 必是叶。否则切成四块，若四个孩子都是叶且 `val` 相同，合并成一个叶；否则建非叶，`val` 可任意（常写 `True`）。

先扫整块再决定是否切也行，但每个格子在每一层都被扫，多一个 $\log n$。先切再合并是 $O(n^2)$。

## 参考代码

```python
from typing import List


class Node:
    def __init__(self, val, isLeaf, topLeft=None, topRight=None, bottomLeft=None, bottomRight=None):
        self.val = val
        self.isLeaf = isLeaf
        self.topLeft = topLeft
        self.topRight = topRight
        self.bottomLeft = bottomLeft
        self.bottomRight = bottomRight


def construct(grid: List[List[int]]) -> Node:
    def build(r0: int, c0: int, size: int) -> Node:
        if size == 1:
            return Node(bool(grid[r0][c0]), True)
        h = size // 2
        tl, tr = build(r0, c0, h), build(r0, c0 + h, h)
        bl, br = build(r0 + h, c0, h), build(r0 + h, c0 + h, h)
        if tl.isLeaf and tr.isLeaf and bl.isLeaf and br.isLeaf and tl.val == tr.val == bl.val == br.val:
            return Node(tl.val, True)
        return Node(True, False, tl, tr, bl, br)

    return build(0, 0, len(grid))


if __name__ == "__main__":
    a = construct([[1, 1], [1, 1]])
    assert a.isLeaf and a.val is True
    b = construct([[0]])
    assert b.isLeaf and b.val is False
    c = construct([[0, 1], [1, 0]])
    assert not c.isLeaf
    assert c.topLeft.isLeaf and c.topLeft.val is False
    assert c.topRight.isLeaf and c.topRight.val is True
    assert c.bottomLeft.isLeaf and c.bottomLeft.val is True
    assert c.bottomRight.isLeaf and c.bottomRight.val is False
    print("ok")
```

## 复杂度

时间 $O(n^2)$，每个格子进入常数次。递归深度 $O(\log n)$。

## 边界

- $n=1$：`size == 1` 直接成叶，`val` 为该格的布尔值。
- 整图全 $0$ / 全 $1$：四分后四个孩子都是同值叶，合并成一棵单结点树。
- 只有一格不同：从根一路切到那一格，其他三个象限仍可合成叶。

## 追问

- **孩子顺序？** 题目规定四个孩子依次是左上、右上、左下、右下，对应 `(r0, c0)`、`(r0, c0+h)`、`(r0+h, c0)`、`(r0+h, c0+h)`。写成左上/左下/右上/右下（行列优先）会整树镜像，判题全错。非叶的 `val` 任意，常用 `True`，判题只看 `isLeaf` 和孩子。

```python
h = size // 2
tl = build(r0, c0, h)
tr = build(r0, c0 + h, h)
bl = build(r0 + h, c0, h)
br = build(r0 + h, c0 + h, h)
```

- **二维前缀和提前判全同？** 先 $O(n^2)$ 做二维前缀，一块和为 $0$ 或 `size*size` 则全同，直接建叶、不再四分。均匀大块时结点更少；最坏仍每格都切到 $1\times 1$，时间仍 $O(n^2)$。现写法「先切再合并」也是 $O(n^2)$，前缀和只是少一次合并、实现更长。

```python
def constructPrefix(grid):
    n = len(grid)
    pre = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(n):
            pre[i + 1][j + 1] = pre[i][j + 1] + pre[i + 1][j] - pre[i][j] + grid[i][j]

    def same(r0, c0, size):
        r1, c1 = r0 + size, c0 + size
        s = pre[r1][c1] - pre[r0][c1] - pre[r1][c0] + pre[r0][c0]
        return s == 0 or s == size * size, bool(s)

    def build(r0, c0, size):
        ok, val = same(r0, c0, size)
        if ok:
            return Node(val, True)
        h = size // 2
        return Node(True, False,
                    build(r0, c0, h), build(r0, c0 + h, h),
                    build(r0 + h, c0, h), build(r0 + h, c0 + h, h))

    return build(0, 0, n)
```
