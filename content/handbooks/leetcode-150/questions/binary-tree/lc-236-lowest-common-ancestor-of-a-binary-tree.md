---
id: lc-236-lowest-common-ancestor-of-a-binary-tree
section: binary-tree
order: 14
level: S
title: LC 236 · 二叉树的最近公共祖先
quick: >-
  普通二叉树，不是 BST。碰到 `p`/`q` 或空就返回。左右都非空则当前是 LCA；只有一侧非空，答案在那侧。时间
  $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 236. 二叉树的最近公共祖先
    url: https://leetcode.cn/problems/lowest-common-ancestor-of-a-binary-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

在普通二叉树里找 `p` 和 `q` 的最近公共祖先。题保证节点都在树上；一个节点可以是自己的祖先。值互异。

## 思路

递归函数返回子树中找到的目标节点或已确定的祖先。当前是 `None`、`p` 或 `q` 时直接返回；否则分别递归左右子树。两侧都有结果，说明目标分居左右，当前节点就是最近公共祖先（LCA）。只有一侧有结果，就将该结果继续向上返回。

常见误区是：当成 BST 用值比较走单路。那是 LC 235。这里必须两边都看。

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


def lowestCommonAncestor(
    root: Optional[TreeNode],
    p: TreeNode,
    q: TreeNode,
) -> Optional[TreeNode]:
    if root is None or root is p or root is q:
        return root
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    if left and right:
        return root
    return left or right


if __name__ == "__main__":
    n7, n4 = TreeNode(7), TreeNode(4)
    n2 = TreeNode(2, n7, n4)
    n6, n0, n8 = TreeNode(6), TreeNode(0), TreeNode(8)
    n5, n1 = TreeNode(5, n6, n2), TreeNode(1, n0, n8)
    root = TreeNode(3, n5, n1)
    assert lowestCommonAncestor(root, n5, n1) is root
    assert lowestCommonAncestor(root, n5, n4) is n5
    assert lowestCommonAncestor(root, n7, n4) is n2
    print("ok")
```

## 复杂度

时间 $O(n)$，最坏扫完整棵。额外空间 $O(h)$。

## 边界

- `p` 是 `q` 的祖先：碰到 `p` 就返回，不必再往下找 `q`。
- `p`、`q` 是根的左右孩子：根就是 LCA。
- 链状树：LCA 是更靠上的那个。

## 追问

- **树是 BST（LC 235）？** 按值分流即可，不必两边都搜。从根往下：二者都小于当前走左，都大于走右，否则当前就是分叉点（其中一个就是当前也算）。平均 $O(h)$，可以写成迭代。本题不是 BST，值大小和拓扑无关。

```python
def lowestCommonAncestor(root, p, q):
    while root:
        if p.val < root.val and q.val < root.val:
            root = root.left
        elif p.val > root.val and q.val > root.val:
            root = root.right
        else:
            return root
```

- **`p` 或 `q` 可能不在树里？** 本题保证都在。若不一定在，不能「碰到一个就返回」，另一侧可能根本没有目标。后序应返回「找到了几个」：左右加自身命中数，恰好 $2$ 个且还没记过时，当前才是 LCA；最终命中不足 $2$ 就返回空。

```python
def lca_maybe_absent(root, p, q):
    found = [None]

    def dfs(node):
        if node is None:
            return 0
        n = dfs(node.left) + dfs(node.right) + (node is p or node is q)
        if n == 2 and found[0] is None:
            found[0] = node
        return n

    dfs(root)
    return found[0]
```
