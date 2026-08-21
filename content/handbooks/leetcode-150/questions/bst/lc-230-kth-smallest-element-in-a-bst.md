---
id: lc-230-kth-smallest-element-in-a-bst
section: bst
order: 2
level: S
title: LC 230 · 二叉搜索树中第K小的元素
quick: >-
  中序第 $k$ 个就是答案。受控中序，数到 $k$ 停。时间平均 $O(h+k)$，额外空间
  $O(h)$。
tags:
  - Tree
  - BST
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 230. 二叉搜索树中第K小的元素
    url: https://leetcode.cn/problems/kth-smallest-element-in-a-bst/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定 BST 与正整数 $k$，返回其中第 $k$ 小的节点值（$1$-indexed）。

## 思路

BST 中序递增，第 $k$ 次访问就是答案。用计数或栈做受控中序，到 $k$ 立刻返回，不必走完整棵。

若节点带子树规模，可按左子树大小二分：$k \le \text{leftSize}$ 走左，相等取根，否则 $k$ 减去左和根再走右。

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


def kthSmallest(root: Optional[TreeNode], k: int) -> int:
    stack = []
    cur = root
    while True:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.right


if __name__ == "__main__":
    root = TreeNode(3, TreeNode(1, None, TreeNode(2)), TreeNode(4))
    assert kthSmallest(root, 1) == 1
    assert kthSmallest(root, 3) == 3
    root2 = TreeNode(5, TreeNode(3, TreeNode(2, TreeNode(1)), TreeNode(4)), TreeNode(6))
    assert kthSmallest(root2, 3) == 3
    print("ok")
```

## 复杂度

时间最坏 $O(n)$，平衡时约 $O(h+k)$。额外空间 $O(h)$。

## 边界

- $k=1$：最左节点，最小值。
- $k=n$：最右节点，最大值。
- 左链很深：栈或递归 $O(h)$，最坏 $O(n)$。

## 追问

- **第 $k$ 大？** 中序反向：一直向右压栈，弹出后走左孩子的右链，数到 $k$ 停。或先数节点总数 $n$，再求第 $n-k+1$ 小（多一次 $O(n)$ 计数）。反向中序不必先知道 $n$。

```python
def kthLargest(root, k):
    stack, cur = [], root
    while True:
        while cur:
            stack.append(cur)
            cur = cur.right
        cur = stack.pop()
        k -= 1
        if k == 0:
            return cur.val
        cur = cur.left
```

- **频繁查询、树会插入删除？** 给每个节点维护子树规模 `size`。查询：`leftSize = root.left.size if root.left else 0`；若 $k \le leftSize$ 走左；若 $k = leftSize+1$ 返回根；否则 $k \gets k-leftSize-1$ 走右。每次 $O(h)$。插入删除同步改 `size`。和 BST 迭代器同一中序思想，但迭代器适合「顺序吐出」，`size` 适合随机第 $k$ 次。独立卡见 `lc-173-binary-search-tree-iterator`。

```python
def kthSmallest_with_size(root, k):
    while root:
        left = root.left.size if root.left else 0
        if k <= left:
            root = root.left
        elif k == left + 1:
            return root.val
        else:
            k -= left + 1
            root = root.right
```
