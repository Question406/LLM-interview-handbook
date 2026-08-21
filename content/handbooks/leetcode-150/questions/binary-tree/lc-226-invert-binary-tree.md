---
id: lc-226-invert-binary-tree
section: binary-tree
order: 3
level: S
title: LC 226 · 翻转二叉树
quick: >-
  每个节点交换左右孩子，再递归翻转两棵子树。前序或后序都行。时间 $O(n)$，额外空间
  $O(h)$。
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 226. 翻转二叉树
    url: https://leetcode.cn/problems/invert-binary-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

翻转整棵二叉树：每个节点的左右子树互换。返回新根（仍是原根对象）。

## 思路

碰到节点就交换 `left` 与 `right`，再对两个孩子递归。空节点直接返回。

交换与递归谁先谁后都行：先交换再递归，或先翻转子树再交换，结果一样。面试说清「每个节点交换一次」。

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

时间 $O(n)$，每个节点交换一次。额外空间 $O(h)$。

## 边界

- 空树：返回 `None`。
- 单节点：左右都空，交换无效果。
- 只有左孩子或只有右孩子：交换后挂到另一侧。

## 追问

- **必须原地？** 上面已经原地改指针，不必 `new` 节点。若禁止改原树，递归新建：`return TreeNode(root.val, invert(root.right), invert(root.left))`，额外 $O(n)$ 节点。面试先问清是否共享原对象。

- **层序翻转？** 队列弹出当前节点，交换 `left`/`right`，再把（交换后的）非空孩子入队。每个节点仍只处理一次，时间 $O(n)$，额外空间 $O(w)$。和 DFS 等价，只是遍历顺序不同。

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
