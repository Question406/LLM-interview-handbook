---
id: lc-222-count-complete-tree-nodes
section: binary-tree
order: 13
level: A
title: LC 222 · 完全二叉树的节点个数
quick: >-
  完全二叉树：左右高度相同则是满树，节点数 $2^h-1$；否则 $1+$ 递归左右。高度沿边走 $O(h)$。时间
  $O(h^2)$，额外空间 $O(h)$。
tags:
  - Tree
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 222. 完全二叉树的节点个数
    url: https://leetcode.cn/problems/count-complete-tree-nodes/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定完全二叉树，返回节点个数。完全：除最后一层外全满，最后一层节点靠左。

## 思路

普通 DFS 计数 $O(n)$ 能过，但面试要吃「完全」。沿左孩子量左高、沿右孩子量右高（这里高按节点个数）。两高相等则满树，直接 $2^h-1$。不等则根加一，再递归左右——其中一侧必是满的，递归会很快收掉。

也可以对最后一层编号二分：看中位路径是否存在，时间同样 $O(h^2)$。

## 参考代码

```python
from __future__ import annotations

from typing import Optional


class TreeNode:
    def __init__(
        self,
        val: int = 0,
        left: Optional["TreeNode"] = None,
        right: Optional["TreeNode"] = None,
    ):
        self.val = val
        self.left = left
        self.right = right


def countNodes(root: Optional[TreeNode]) -> int:
    def height(node: Optional[TreeNode], go_left: bool) -> int:
        h = 0
        while node:
            h += 1
            node = node.left if go_left else node.right
        return h

    if root is None:
        return 0
    lh, rh = height(root, True), height(root, False)
    if lh == rh:
        return (1 << lh) - 1
    return 1 + countNodes(root.left) + countNodes(root.right)


if __name__ == "__main__":
    root = TreeNode(
        1,
        TreeNode(2, TreeNode(4), TreeNode(5)),
        TreeNode(3, TreeNode(6)),
    )
    assert countNodes(root) == 6
    assert countNodes(None) == 0
    assert countNodes(TreeNode(1)) == 1
    print("ok")
```

## 复杂度

每层量高 $O(h)$，递归深度 $O(h)$，总共 $O(h^2)$。满树一次量高即停。额外空间 $O(h)$。

## 边界

- 空树：返回 $0$。
- $n=1$：满树公式 $2^1-1=1$。
- 刚满的一层：左右高相等，一次公式结束。
- 最后一层只有最左一个：左右高差 $1$，递归左是满的、右几乎为空。

## 追问

- **普通二叉树、不是完全？** 满树公式失效，只能 $O(n)$ 遍历：`1 + count(left) + count(right)`。完全性保证「缺口只出现在最后一层靠右」，才能用高度相等判定满树。

- **对最后一层二分？** 先沿左孩子量高 $h$（边数）。上层满节点 $2^h-1$，最后一层下标 $[0, 2^h-1]$。`exists(idx)` 从根走 $h$ 步：把区间对半，`idx` 落左半走左、否则走右。对下标二分找第一个不存在的位置，存在的个数加到上层。每次判定 $O(h)$、二分 $O(h)$ 次，仍 $O(h^2)$。

```python
def countNodes(root):
    if root is None:
        return 0
    h, node = 0, root
    while node.left:
        h += 1
        node = node.left

    def exists(idx):
        left, right, cur = 0, (1 << h) - 1, root
        for _ in range(h):
            mid = (left + right) // 2
            if idx <= mid:
                cur = cur.left
                right = mid
            else:
                cur = cur.right
                left = mid + 1
        return cur is not None

    lo, hi = 0, (1 << h) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if exists(mid):
            lo = mid + 1
        else:
            hi = mid - 1
    return ((1 << h) - 1) + lo
```
