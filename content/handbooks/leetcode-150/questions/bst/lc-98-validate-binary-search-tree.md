---
id: lc-98-validate-binary-search-tree
section: bst
order: 3
level: S
title: LC 98 · 验证二叉搜索树
quick: >-
  带上下界递归：左子树必须 $\lt$ 当前值，右子树必须 $\gt$ 当前值，边界沿路径收紧。或中序严格递增。时间
  $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - BST
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 98. 验证二叉搜索树
    url: https://leetcode.cn/problems/validate-binary-search-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

判断二叉树是否是有效 BST：每个节点左子树所有值严格小于它，右子树所有值严格大于它。

## 思路

只比「和左右孩子」不够，还要满足整棵子树相对祖先的上下界。递归带 `(lo, hi)`，当前值必须落在开区间内，左孩子继承 `(lo, val)`，右孩子继承 `(val, hi)`。

中序必须严格递增，维护前驱也能验。值可能是 `INT_MIN` / `INT_MAX`，用空边界或 `None`，不要写成 `node.val > INT_MIN` 这种硬编码。

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


def isValidBST(root: Optional[TreeNode]) -> bool:
    def dfs(node: Optional[TreeNode], lo: Optional[int], hi: Optional[int]) -> bool:
        if node is None:
            return True
        if lo is not None and node.val <= lo:
            return False
        if hi is not None and node.val >= hi:
            return False
        return dfs(node.left, lo, node.val) and dfs(node.right, node.val, hi)

    return dfs(root, None, None)


if __name__ == "__main__":
    assert isValidBST(TreeNode(2, TreeNode(1), TreeNode(3)))
    bad = TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))
    assert not isValidBST(bad)
    sneak = TreeNode(5, TreeNode(4), TreeNode(6, TreeNode(3), TreeNode(7)))
    assert not isValidBST(sneak)
    assert isValidBST(TreeNode(1))
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(h)$。

## 边界

- 单节点：有效。
- 重复值：本题必须严格，相等即无效。
- 右子树里藏了一个比祖先还小的节点：只比父子会漏掉。

## 追问

- **只检查左右孩子大小？** 漏掉隔代约束。反例：`[5,4,6,null,null,3,7]`，根左右都合法，但 $3$ 在右子树却小于 $5$。必须把祖先上下界沿路径收紧，或中序严格递增。

```python
def isValidBST_inorder(root):
    prev = None

    def dfs(node):
        nonlocal prev
        if node is None:
            return True
        if not dfs(node.left):
            return False
        if prev is not None and node.val <= prev:
            return False
        prev = node.val
        return dfs(node.right)

    return dfs(root)
```

- **允许等于（非严格 BST）？** 把开区间改成闭：左界判断改成 `node.val < lo` 才失败，右界 `node.val > hi`；中序改成非严格递增 `node.val < prev` 才失败。本题题面是严格，面试先确认。值可能是 $32$ 位最值，边界用 `None` 而不是 `INT_MIN`。
