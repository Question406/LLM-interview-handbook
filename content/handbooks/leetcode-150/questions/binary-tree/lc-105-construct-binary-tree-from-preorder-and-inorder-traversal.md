---
id: lc-105-construct-binary-tree-from-preorder-and-inorder-traversal
section: binary-tree
order: 5
level: S
title: LC 105 · 从前序与中序遍历序列构造二叉树
quick: >-
  `pre[0]` 是根。在中序里切开左右子树，再按长度切前序。哈希记下中序下标，避免每次扫描。时间
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
  - title: 105. 从前序与中序遍历序列构造二叉树
    url: https://leetcode.cn/problems/construct-binary-tree-from-preorder-and-inorder-traversal/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定一棵树的前序与中序遍历（节点值互异），还原这棵二叉树。

## 思路

前序第一个是根。中序里根左边是左子树，右边是右子树。左子树大小为 $k$，则前序下一段 $k$ 个是左子树，再往后是右子树。递归构造。

中序下标预处理成哈希，每次 $O(1)$ 定位根。白板我会先画「`pre[0]` 定根、中序分左右」，再写下标区间。

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


def buildTree(preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
    idx: Dict[int, int] = {v: i for i, v in enumerate(inorder)}

    def build(pre_l: int, pre_r: int, in_l: int, in_r: int) -> Optional[TreeNode]:
        if pre_l > pre_r:
            return None
        root_val = preorder[pre_l]
        root = TreeNode(root_val)
        mid = idx[root_val]
        left_size = mid - in_l
        root.left = build(pre_l + 1, pre_l + left_size, in_l, mid - 1)
        root.right = build(pre_l + left_size + 1, pre_r, mid + 1, in_r)
        return root

    n = len(preorder)
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
    root = buildTree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
    assert to_list(root) == [3, 9, 20, None, None, 15, 7]
    assert to_list(buildTree([-1], [-1])) == [-1]
    print("ok")
```

## 复杂度

时间 $O(n)$，每个节点建一次。哈希 $O(n)$，递归栈 $O(h)$。

## 边界

- 单节点：前序、中序都是同一个值。
- 全是左链：中序里根在最右，左段吃掉前序剩余全部。
- 全是右链：中序里根在最左，左段长度为 $0$。

## 追问

- **节点值有重复？** 单靠前序+中序不能唯一确定：中序里同一个值可能对应多个下标，根的切分有歧义。本题保证互异，才能预处理 `val -> index`。若允许重复，还要额外约束（例如给出父指针或唯一编号）。

- **后序 + 中序（LC 106）？** 后序最后一个才是根，中序同样切左右。右子树大小 $k=\text{in}_r-\text{mid}$，后序 `[post_r-k, post_r-1]` 是右子树，更前面是左子树。和本题对称：前序根在头、先建左；后序根在尾、先算右段长度。独立卡见 `lc-106-construct-binary-tree-from-inorder-and-postorder-traversal`。

```python
def buildTree(inorder, postorder):
    idx = {v: i for i, v in enumerate(inorder)}

    def build(in_l, in_r, post_l, post_r):
        if post_l > post_r:
            return None
        root = TreeNode(postorder[post_r])
        mid = idx[root.val]
        k = in_r - mid
        root.left = build(in_l, mid - 1, post_l, post_r - k - 1)
        root.right = build(mid + 1, in_r, post_r - k, post_r - 1)
        return root

    n = len(inorder)
    return build(0, n - 1, 0, n - 1)
```
