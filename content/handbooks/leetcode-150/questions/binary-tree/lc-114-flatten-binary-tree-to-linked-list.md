---
id: lc-114-flatten-binary-tree-to-linked-list
section: binary-tree
order: 8
level: A
title: LC 114 · 二叉树展开为链表
quick: >-
  按前序把树原地摊成一条右链，所有 `left` 置空。先摊左右，再把左链接到根右、原右链接到左链尾。时间
  $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 114. 二叉树展开为链表
    url: https://leetcode.cn/problems/flatten-binary-tree-to-linked-list/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

把二叉树原地展开为单链表：顺序等于前序遍历，只用 `right` 连接，所有 `left` 为 `None`。

## 思路

后序先把左右都摊成右链。记下原右链，把左链接到 `root.right`，`left` 清空，再沿右链走到尾，接上原右链。

也可以先序用栈，或 Morris：把右子树接到左子树最右，再把整段左子树旋到右边。白板我会先讲「前序顺序 + 原地右链」。

## 参考代码

```python
from __future__ import annotations

from typing import List, Optional


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


def flatten(root: Optional[TreeNode]) -> None:
    if root is None:
        return
    flatten(root.left)
    flatten(root.right)
    right = root.right
    root.right = root.left
    root.left = None
    cur = root
    while cur.right:
        cur = cur.right
    cur.right = right


def right_chain(root: Optional[TreeNode]) -> List[int]:
    vals: List[int] = []
    while root:
        assert root.left is None
        vals.append(root.val)
        root = root.right
    return vals


if __name__ == "__main__":
    root = TreeNode(
        1,
        TreeNode(2, TreeNode(3), TreeNode(4)),
        TreeNode(5, None, TreeNode(6)),
    )
    flatten(root)
    assert right_chain(root) == [1, 2, 3, 4, 5, 6]
    empty = None
    flatten(empty)
    assert empty is None
    print("ok")
```

## 复杂度

时间 $O(n)$。递归版找右链尾会重复走，最坏仍 $O(n)$（每个边走常数次）。额外空间 $O(h)$；Morris 可到 $O(1)$。

## 边界

- 空树：直接返回。
- 只有右链：已经是答案，左指针全空。
- 只有左链：整段旋到 `right` 上，`left` 清空。

## 追问

- **不能用 $O(h)$ 栈 / 递归（Morris）？** 前序展开：若当前有左子树，找到左子树最右节点（前驱），把它的 `right` 接到当前的原右子树，再把左子树整体接到 `cur.right`，`left` 置空。然后 `cur` 沿右链走下一步。每个节点的右指针最多被改常数次，时间 $O(n)$，额外空间 $O(1)$。

```python
def flatten(root):
    cur = root
    while cur:
        if cur.left:
            pred = cur.left
            while pred.right:
                pred = pred.right
            pred.right = cur.right
            cur.right = cur.left
            cur.left = None
        cur = cur.right
```

- **允许新开链表？** 先前序遍历把节点放进数组（或边走边串新节点），再按顺序把 `right` 指下一个、`left` 置空。时间 $O(n)$，额外空间 $O(n)$。白板当备选；题面要求原地时还是后序拼接或 Morris。
