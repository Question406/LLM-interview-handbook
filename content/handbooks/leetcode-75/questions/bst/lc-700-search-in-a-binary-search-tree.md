---
id: lc-700-search-in-a-binary-search-tree
section: bst
order: 1
level: A
title: LC 700 · 二叉搜索树中的搜索
quick: "从根开始比较目标值和当前节点值：目标更小就走左子树，更大就走右子树，相等就返回该节点。BST 搜索只走一条路径，迭代时间 $O(h)$，额外空间 $O(1)$。"
tags:
  - Tree
  - BST
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 700. Search in a Binary Search Tree
    url: https://leetcode.com/problems/search-in-a-binary-search-tree/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给 BST 的根和整数 `val`，找到值等于 `val` 的节点，返回以它为根的子树；不存在返回 `None`。节点数 $[1, 5000]$，值互异。

## 思路

BST 性质：左子树所有值小于根，右子树所有值大于根。所以每次和当前节点比较就能排除一半子树：`val` 更小只可能在左边，更大只可能在右边。走到 `None` 就是不存在。

普通二叉树的搜索要 DFS 全树，$O(n)$。BST 只走一条根到叶的路径，$O(h)$；平衡时 $O(\log n)$，退化成链时仍是 $O(n)$。递归写法是尾递归，我会直接写成 `while` 循环，省掉栈。

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


def searchBST(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    while root and root.val != val:
        root = root.left if val < root.val else root.right
    return root


if __name__ == "__main__":
    root = build_tree([4, 2, 7, 1, 3])
    assert to_level_list(searchBST(root, 2)) == [2, 1, 3]
    assert searchBST(root, 5) is None
    assert searchBST(root, 4) is root
    assert to_level_list(searchBST(root, 7)) == [7]
    assert searchBST(build_tree([1]), 0) is None
    print("ok")
```

## 复杂度

时间 $O(h)$，平衡 $O(\log n)$，最坏 $O(n)$。额外空间 $O(1)$。

## 边界

- 目标是根：循环不进，直接返回根。
- 目标不存在：走到 `None` 返回。
- 退化成链：仍正确，只是 $O(n)$。

## 追问

- **插入一个新值（LC 701）？** 同样按值走单路，走到空位置挂新节点。新值保证不存在，插成叶子即可，不需要旋转。时间 $O(h)$。

```python
def insertIntoBST(root, val):
    node = TreeNode(val)
    if root is None:
        return node
    cur = root
    while True:
        if val < cur.val:
            if cur.left is None:
                cur.left = node
                break
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = node
                break
            cur = cur.right
    return root
```

- **找不到时返回最接近的值（LC 270）？** 同一条搜索路径上边走边更新 `abs(node.val - target)` 最小的节点。最接近的值一定在这条路径上：离开某节点往一侧走时，另一侧子树整体更远。删除节点（`lc-450-delete-node-in-a-bst`）也是先用这套走法定位。
