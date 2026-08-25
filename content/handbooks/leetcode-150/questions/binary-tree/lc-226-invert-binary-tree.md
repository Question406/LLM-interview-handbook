---
id: lc-226-invert-binary-tree
section: binary-tree
order: 3
level: S
title: LC 226 · 翻转二叉树
quick: >-
  我会在每个节点把左右孩子换掉，再递归翻两边子树。前序后序都行。时间 $O(n)$，额外空间
  $O(h)$。
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 226. 翻转二叉树
    url: https://leetcode.cn/problems/invert-binary-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

把整棵二叉树左右对调。返回的还是原来那个根对象。

## 思路

碰到一个节点，就把 `left` 和 `right` 换掉，再对两个孩子递归。空节点直接返回。

先换再递归，或先翻子树再换，结果一样。白板我会补一句：每个节点只交换一次。

## 参考代码

```python
from __future__ import annotations

from collections import deque
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


def invertTree(root: Optional[TreeNode]) -> Optional[TreeNode]:
    if root is None:
        return None
    root.left, root.right = root.right, root.left
    invertTree(root.left)
    invertTree(root.right)
    return root


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
    root = TreeNode(
        4,
        TreeNode(2, TreeNode(1), TreeNode(3)),
        TreeNode(7, TreeNode(6), TreeNode(9)),
    )
    assert to_list(invertTree(root)) == [4, 7, 2, 9, 6, 3, 1]
    assert invertTree(None) is None
    print("ok")
```

## 复杂度

时间 $O(n)$，每个节点换一次。额外空间 $O(h)$。

## 边界

- 空树：返回 `None`。
- 单节点：左右都空，换了等于没换。
- 只有左孩子或只有右孩子：换完会挂到另一侧。

## 追问

- **必须原地？** 上面已经原地改指针，不必 `new` 节点。若不许改原树，递归新建：`return TreeNode(root.val, invert(root.right), invert(root.left))`，额外 $O(n)$ 个节点。我会先问清返不返回原对象。

- **层序翻转？** 队列弹出当前节点，交换 `left`/`right`，再把交换后的非空孩子入队。每个节点仍只处理一次，时间 $O(n)$，额外空间 $O(w)$。和 DFS 结果一样，只是遍历顺序不同。

```python
from collections import deque

def invertTree(root):
    if root is None:
        return None
    q = deque([root])
    while q:
        node = q.popleft()
        node.left, node.right = node.right, node.left
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
    return root
```
