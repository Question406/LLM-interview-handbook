---
id: lc-102-binary-tree-level-order-traversal
section: binary-tree-bfs
order: 3
level: S
title: LC 102 · 二叉树的层序遍历
quick: >-
  队列 BFS，每层先记下 `size`，只弹出这么多个，正好一层。空根返回空。时间 $O(n)$，额外空间
  $O(w)$。
tags:
  - Tree
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 102. 二叉树的层序遍历
    url: https://leetcode.cn/problems/binary-tree-level-order-traversal/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

按层返回二叉树节点值，每一层一个列表，从根到叶、每层从左到右。

## 思路

队列先放根。每一轮开始记下 `size=len(q)`，只弹出这么多个，收集成一层，同时把左右孩子入队。空根直接 `[]`。

不要一次掏光队列再事后切层。面试强调「用当轮 `size` 切开」。

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


def levelOrder(root: Optional[TreeNode]) -> List[List[int]]:
    if root is None:
        return []
    q = deque([root])
    ans: List[List[int]] = []
    while q:
        level: List[int] = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(level)
    return ans


if __name__ == "__main__":
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert levelOrder(root) == [[3], [9, 20], [15, 7]]
    assert levelOrder(TreeNode(1)) == [[1]]
    assert levelOrder(None) == []
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(w)$，完全二叉树底层最宽。

## 边界

- 空树：返回 `[]`，不是 `[[]]`。
- 单节点：一层一个值。
- 只有左链：每层恰好一个节点。

## 追问

- **自底向上层序（LC 107）？** 先按本题从根到叶收集，最后把外层列表反转（或每层 `appendleft` / 插到下标 $0$）。层内仍从左到右，只是层的顺序反过来。时间 $O(n)$。不要在队列里从叶往根走——没有父指针。

```python
from collections import deque

def levelOrderBottom(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        level = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(level)
    ans.reverse()
    return ans
```

- **改成 DFS？** 按深度把值塞进对应桶：进入节点时若 `d == len(ans)` 就新开一层，再先左后右。结果与 BFS 相同。能过题，但面试先声明标准答案是切层 BFS；DFS 栈深最坏 $O(n)$，宽树时 BFS 才吃宽度。

```python
def levelOrder_dfs(root):
    ans = []

    def dfs(node, d):
        if node is None:
            return
        if d == len(ans):
            ans.append([])
        ans[d].append(node.val)
        dfs(node.left, d + 1)
        dfs(node.right, d + 1)

    dfs(root, 0)
    return ans
```
