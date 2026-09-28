---
id: lc-100-same-tree
section: binary-tree
order: 2
level: A
title: LC 100 · 相同的树
quick: >-
  两棵树同时 DFS：都空则同；一个空或值不同则否；否则左右子树都相同。时间 $O(n)$，额外空间
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
  - title: 100. 相同的树
    url: https://leetcode.cn/problems/same-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

判断两棵二叉树是否结构相同且对应节点值相等。

## 思路

同步递归。`p`、`q` 都是 `None` 则相同；恰好一个是 `None` 或 `val` 不同则否；否则继续比左右。

结构和值一起比，不要只序列化值。层序同时出队也可以。

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


def isSameTree(p: Optional[TreeNode], q: Optional[TreeNode]) -> bool:
    if p is None or q is None:
        return p is q
    return (
        p.val == q.val
        and isSameTree(p.left, q.left)
        and isSameTree(p.right, q.right)
    )


if __name__ == "__main__":
    a = TreeNode(1, TreeNode(2), TreeNode(3))
    b = TreeNode(1, TreeNode(2), TreeNode(3))
    assert isSameTree(a, b)
    c = TreeNode(1, TreeNode(2), None)
    d = TreeNode(1, None, TreeNode(2))
    assert not isSameTree(c, d)
    assert isSameTree(None, None)
    print("ok")
```

## 复杂度

时间 $O(\min(n_p,n_q))$，一旦分叉即可停。额外空间 $O(h)$。

## 边界

- 都空：结构和值都真空，判相同。
- 恰好一棵空：结构已经不同。
- 结构相同但某节点值不同。
- 镜像树（一边挂左、一边挂右）：值看起来像，结构不同，应判否。

## 追问

- **只比值、不管结构？** 不够。只收集非空值时，`[1,2]` 与 `[1,null,2]` 都会得到 $1,2$，但一棵左孩子、一棵右孩子。必须同步走两个指针：都空才算同，一个空一个非空直接否，值不等也否，再同时比左右。若坚持序列化，必须带上空位标记（例如 `val,#`），仍是结构和值一起编码。

- **一棵是另一棵的子树（LC 572）？** 在 `root` 上每个节点当起点，调用本题的「相同树」。外层 DFS 枚举起点，内层 `same` 同步比结构和值。时间最坏 $O(nm)$。空 `subRoot` 视为真；`root` 空而子树非空为假。

```python
def isSubtree(root, subRoot):
    def same(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and same(a.left, b.left) and same(a.right, b.right)

    if root is None:
        return subRoot is None
    return (
        same(root, subRoot)
        or isSubtree(root.left, subRoot)
        or isSubtree(root.right, subRoot)
    )
```
