---
id: lc-106-construct-binary-tree-from-inorder-and-postorder-traversal
section: binary-tree
order: 6
level: A
title: LC 106 · 从中序与后序遍历序列构造二叉树
quick: >-
  `post[-1]` 是根。中序切开左右，后序末段长度等于右子树大小。哈希定位中序下标。时间
  $O(n)$，额外空间 $O(n)$。
tags:
  - Tree
  - Hash Table
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 106. 从中序与后序遍历序列构造二叉树
    url: https://leetcode.cn/problems/construct-binary-tree-from-inorder-and-postorder-traversal/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定一棵树的中序与后序遍历（节点值互异），还原这棵二叉树。

## 思路

后序最后一个是根。中序里根左边是左子树，右边是右子树。右子树大小为 $k$，则后序倒数第 $2$ 到倒数第 $k+1$ 是右子树，更前面是左子树。

和 LC 105 对称：前序根在头，后序根在尾。

## 参考代码

```python
from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional


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


def buildTree(inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
    idx: Dict[int, int] = {v: i for i, v in enumerate(inorder)}

    def build(in_l: int, in_r: int, post_l: int, post_r: int) -> Optional[TreeNode]:
        if post_l > post_r:
            return None
        root_val = postorder[post_r]
        root = TreeNode(root_val)
        mid = idx[root_val]
        right_size = in_r - mid
        root.left = build(in_l, mid - 1, post_l, post_r - right_size - 1)
        root.right = build(mid + 1, in_r, post_r - right_size, post_r - 1)
        return root

    n = len(inorder)
    return build(0, n - 1, 0, n - 1)


def to_list(root: Optional[TreeNode]) -> List[Optional[int]]:
    if root is None:
        return []
    out: List[Optional[int]] = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


if __name__ == "__main__":
    root = buildTree([9, 3, 15, 20, 7], [9, 15, 7, 20, 3])
    assert to_list(root) == [3, 9, 20, None, None, 15, 7]
    assert to_list(buildTree([-1], [-1])) == [-1]
    print("ok")
```

## 复杂度

时间 $O(n)$，哈希 $O(n)$，递归栈 $O(h)$。

## 边界

- 单节点：中序、后序都是同一个值。
- 只有左子树：后序根仍在最后，中序根在最右，右段长度 $0$。
- 只有右子树：中序根在最左，后序除根外整段都是右子树。

## 追问

- **前序 + 后序、没有中序？** 一般不能唯一确定。前序 `根|左|右`、后序 `左|右|根`，左右交界在哪不知道；`[1,2]` 前序配 `[2,1]` 后序，既可以 $2$ 在左也可以在右。满二叉树、或另给一种遍历，才能唯一还原。

- **和前序+中序（LC 105）对照？** 中序负责切开左右，长度算法相同。差别只在根的位置：前序取 `pre[pre_l]`，左子树占前序接下来 $k$ 个；后序取 `post[post_r]`，右子树占后序末尾 $k$ 个。独立卡见 `lc-105-construct-binary-tree-from-preorder-and-inorder-traversal`。

```python
def buildTree(preorder, inorder):
    idx = {v: i for i, v in enumerate(inorder)}

    def build(pre_l, pre_r, in_l, in_r):
        if pre_l > pre_r:
            return None
        root = TreeNode(preorder[pre_l])
        mid = idx[root.val]
        k = mid - in_l
        root.left = build(pre_l + 1, pre_l + k, in_l, mid - 1)
        root.right = build(pre_l + k + 1, pre_r, mid + 1, in_r)
        return root

    n = len(preorder)
    return build(0, n - 1, 0, n - 1)
```
