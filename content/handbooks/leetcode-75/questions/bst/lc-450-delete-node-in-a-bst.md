---
id: lc-450-delete-node-in-a-bst
section: bst
order: 2
level: S
title: LC 450 · 删除二叉搜索树中的节点
quick: >-
  先按值定位。目标缺一个孩子就用另一个孩子顶替；两个孩子都在，就取右子树最小值（后继）覆盖当前值，再去右子树删掉那个后继。递归返回新子树根。时间
  $O(h)$，额外空间 $O(h)$。
tags:
  - Tree
  - BST
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 450. Delete Node in a BST
    url: https://leetcode.com/problems/delete-node-in-a-bst/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给 BST 的根和 `key`，删除值为 `key` 的节点（可能不存在），保持 BST 性质，返回可能变化的根。节点数 $[0, 10^4]$，值互异。进阶要求 $O(h)$。

## 思路

递归函数语义定为「在这棵子树里删掉 `key`，返回删完后的子树根」，父节点用 `root.left = deleteNode(root.left, key)` 接住，就不用单独维护父指针。`key` 小于当前走左，大于走右。命中后分三种：叶子直接返回 `None`；只有一个孩子，返回那个孩子；左右都在，找右子树最左节点（后继，比当前大的最小值），把它的值写到当前节点，再在右子树里递归删掉这个后继。后继没有左孩子，所以第二次删除一定落在前两种情况。

后继顶上来之后，左子树都比它小（原本就小于被删的值），右子树剩下的都比它大，BST 性质保持。用左子树最大值（前驱）也对，结果树不同但都合法。

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


def build_tree(vals: List[Optional[int]]) -> Optional[TreeNode]:
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    q = deque([root])
    i = 1
    while q and i < len(vals):
        node = q.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            q.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            q.append(node.right)
        i += 1
    return root


def to_level_list(root: Optional[TreeNode]) -> List[Optional[int]]:
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


def inorder(root: Optional[TreeNode]) -> List[int]:
    return inorder(root.left) + [root.val] + inorder(root.right) if root else []


def deleteNode(root: Optional[TreeNode], key: int) -> Optional[TreeNode]:
    if root is None:
        return None
    if key < root.val:
        root.left = deleteNode(root.left, key)
    elif key > root.val:
        root.right = deleteNode(root.right, key)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        succ = root.right
        while succ.left:
            succ = succ.left
        root.val = succ.val
        root.right = deleteNode(root.right, succ.val)
    return root


if __name__ == "__main__":
    assert to_level_list(deleteNode(build_tree([5, 3, 6, 2, 4, None, 7]), 3)) == [5, 4, 6, 2, None, None, 7]
    assert to_level_list(deleteNode(build_tree([5, 3, 6, 2, 4, None, 7]), 0)) == [5, 3, 6, 2, 4, None, 7]
    assert to_level_list(deleteNode(build_tree([]), 0)) == []
    assert to_level_list(deleteNode(build_tree([5]), 5)) == []
    assert to_level_list(deleteNode(build_tree([5, 3, 6, 2, 4, None, 7]), 5)) == [6, 3, 7, 2, 4]
    t = deleteNode(build_tree([50, 30, 70, 20, 40, 60, 80, None, None, 35, 45, 55, 65]), 30)
    assert inorder(t) == [20, 35, 40, 45, 50, 55, 60, 65, 70, 80]
    print("ok")
```

## 复杂度

时间 $O(h)$：定位一次，找后继并删除又是一条向下的路径。额外空间 $O(h)$，递归栈。

## 边界

- `key` 不存在：一路走到 `None` 返回，树不变。
- 删根：递归返回值就是新根，调用方必须用返回值，不能假设根不变。
- 删叶子：`left` 为空的分支返回 `right`，即 `None`，叶子自然被摘掉。

## 追问

- **不允许改节点值，只能改指针？** 两个孩子都在时，把后继节点从原位置摘下，再让它接管被删节点的左右子树。摘后继时它的右子树要接回后继的父节点；后继恰好是 `root.right` 时，直接把 `root.left` 挂到它左边。

```python
def deleteNodeRelink(root, key):
    if root is None:
        return None
    if key < root.val:
        root.left = deleteNodeRelink(root.left, key)
        return root
    if key > root.val:
        root.right = deleteNodeRelink(root.right, key)
        return root
    if root.left is None:
        return root.right
    if root.right is None:
        return root.left
    parent, succ = root, root.right
    while succ.left:
        parent, succ = succ, succ.left
    if parent is not root:
        parent.left = succ.right
        succ.right = root.right
    succ.left = root.left
    return succ
```

- **还有更短的写法吗？** 两个孩子都在时，把左子树整体挂到右子树最左节点的左边，返回右子树。正确但树会变高，多次删除后退化得快；面试里我会提一句，主写后继替换。搜索定位的走法见 `lc-700-search-in-a-binary-search-tree`。
