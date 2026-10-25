---
id: lc-427-construct-quad-tree
section: divide-conquer
order: 3
level: A
title: LC 427 · 建立四叉树
quick: "对正方形递归四分：边长为 1 直接成叶，否则先建四个孩子，四个都是叶且 `val` 相同就合成叶 `Node(val, True)`，否则建非叶 `Node(val, False, topLeft, topRight, bottomLeft, bottomRight)`。先切再合并，每格只访问常数次，时间 $O(n^2)$。"
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

## 题目描述

给定 n×n 的二值网格 grid，返回表示整块网格的四叉树根节点。每个节点对应一个正方形区域：如果整个区域取值一致，它是叶节点，val 为该值，四个孩子为空；否则为非叶节点，四个孩子依次表示等大的左上、右上、左下、右下区域。非叶节点的 val 不用于表示区域内容，可以取 0 或 1。

### 接口与输出

实现 `construct(grid: List[List[int]]) -> Node`。Node 包含 `val`、`isLeaf`、`topLeft`、`topRight`、`bottomLeft`、`bottomRight`。返回节点对象，不是序列化数组；示例仅用层序的 `[isLeaf,val]` 对表示一个合法结果。

### 合法输入与约束

`n=2^x`，其中 `0 <= x <= 6`；网格每行长度均为 n，元素为 0 或 1。四叉树必须准确覆盖网格的全部格子。

### 示例

```text
输入：grid = [[0,1],[1,0]]
输出：[[0,1],[1,0],[1,1],[1,1],[1,0]]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/construct-quad-tree/description/)。

## 解题思路与参考答案

## 题意

把 $n\times n$ 的 $0/1$ 网格（$n$ 为 $2$ 的幂）建成四叉树。一块全相同就是叶，`val` 表示这块的取值；否则四个孩子依次是左上、右上、左下、右下。

## 思路

我会递归地先切再合并。一块正方形的结果只取决于它的四个象限，四个象限都已经是同值的叶子时，整块就是一个叶子，不用回头再扫格子。

边长为 $1$ 的块一定是叶。更大的块切成四块分别递归，四个孩子都是叶并且 `val` 相同，就合并成一个叶；否则建非叶，非叶的 `val` 可以任意，常写 `True`。拿 `[[0,1],[1,0]]` 来说，四个 $1\times 1$ 的孩子分别是 `0`、`1`、`1`、`0`，值不全相同，根就是非叶，四个孩子按左上、右上、左下、右下挂上去。

也可以先扫整块，看全不全同再决定切不切，但这样每个格子在每一层都会被扫一次，多出一个 $\log n$ 因子；先切再合并是 $O(n^2)$。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
a = construct([[1, 1], [1, 1]])
assert a.isLeaf and a.val is True
b = construct([[0]])
assert b.isLeaf and b.val is False
c = construct([[0, 1], [1, 0]])
assert not c.isLeaf
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n^2)$，每个格子只进入常数次；递归深度 $O(\log n)$。

## 边界

$n=1$ 时 `size == 1` 直接成叶，`val` 是该格的布尔值。整图全 $0$ 或全 $1$ 时，四分后四个孩子都是同值叶，层层合并成一棵单结点树。只有一格不同时，从根一路切到那一格，其他三个象限仍然各自合成叶。

## 追问

**四个孩子的顺序有讲究吗？**
有。题目规定依次是左上、右上、左下、右下，对应 `(r0, c0)`、`(r0, c0+h)`、`(r0+h, c0)`、`(r0+h, c0+h)`。写成左上、左下、右上、右下（行列优先）会让整棵树镜像，判题全错。非叶的 `val` 任意，常用 `True`，判题只看 `isLeaf` 和孩子。

```python
h = size // 2
tl = build(r0, c0, h)
tr = build(r0, c0 + h, h)
bl = build(r0 + h, c0, h)
br = build(r0 + h, c0 + h, h)
```

**能用二维前缀和提前判断一块是否全同吗？**
能。先花 $O(n^2)$ 建二维前缀和，一块的和为 $0$ 或 `size*size` 就说明全同，直接建叶、不再四分。均匀的大块能少建很多结点；最坏情况仍然每格都切到 $1\times 1$，时间还是 $O(n^2)$。现在「先切再合并」的写法本身也是 $O(n^2)$，前缀和只是省掉一次合并，代码更长。

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
