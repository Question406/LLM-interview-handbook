---
id: lc-1372-longest-zigzag-path-in-a-binary-tree
section: binary-tree-dfs
order: 5
level: A
title: LC 1372 · 二叉树中的最长交错路径
quick: >-
  DFS 给每个节点带两个数：以「最后一步向左」到达它的交错长度 `l`，和「最后一步向右」的 `r`。走左孩子时新长度是
  `r+1`，走右孩子是 `l+1`，反方向重置为 $1$。时间 $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1372. Longest ZigZag Path in a Binary Tree
    url: https://leetcode.com/problems/longest-zigzag-path-in-a-binary-tree/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

交错路径：从任意节点出发，选一个方向（左或右）走到孩子，之后每一步必须换方向，走不动为止。长度是经过的边数，单个节点长度为 $0$。返回树中最长交错路径的长度。节点数 $[1, 5 \times 10^4]$。

## 思路

一条交错路径的延续只取决于「上一步往哪个方向走」。定义到达节点时的两个状态：`l` 是最后一步向左（当前节点是父的左孩子）的交错长度，`r` 是最后一步向右的长度。往左孩子走，上一步必须是向右，新长度 `r + 1`，同时向右的那条链断了，记 $0$；往右孩子走对称，新长度 `l + 1`。每个节点用 `max(l, r)` 更新答案，根从 `(0, 0)` 开始。

容易错的是「换不了方向就归零」：从父节点到这个孩子本身就是一条长度 $1$ 的新交错路径。上面的写法自动覆盖了这点，到左孩子时 `l = r + 1`，至少是 $1$。朴素做法是以每个节点为起点、两个方向各模拟一遍，最坏 $O(n^2)$。

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


def longestZigZag(root: Optional[TreeNode]) -> int:
    ans = 0
    stack = [(root, 0, 0)] if root else []
    while stack:
        node, l, r = stack.pop()
        ans = max(ans, l, r)
        if node.left:
            stack.append((node.left, r + 1, 0))
        if node.right:
            stack.append((node.right, 0, l + 1))
    return ans


if __name__ == "__main__":
    t1 = build_tree([1, None, 1, 1, 1, None, None, 1, 1, None, 1, None, None, None, 1])
    assert longestZigZag(t1) == 3
    t2 = build_tree([1, 1, 1, None, 1, None, None, 1, 1, None, 1])
    assert longestZigZag(t2) == 4
    assert longestZigZag(build_tree([1])) == 0
    assert longestZigZag(build_tree([1, 1, None, 1, None, 1])) == 1
    chain = TreeNode(0)
    cur = chain
    for i in range(1, 50001):
        nxt = TreeNode(i)
        if i % 2:
            cur.left = nxt
        else:
            cur.right = nxt
        cur = nxt
    assert longestZigZag(chain) == 50000
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(h)$，栈里最多一条路径的节点加上兄弟。

## 边界

- 单节点：答案 $0$。
- 全左链：每一步都同方向，答案 $1$，别写成 $0$。
- 完美交错的长链：答案是 $n-1$；这里用显式栈，$5 \times 10^4$ 深也不会爆 Python 递归上限。

## 追问

- **递归写法？** 同样两个状态作为参数，更直观，但链状输入要调高递归上限。

```python
def longestZigZagRec(root):
    ans = 0

    def dfs(node, l, r):
        nonlocal ans
        if node is None:
            return
        ans = max(ans, l, r)
        dfs(node.left, r + 1, 0)
        dfs(node.right, 0, l + 1)

    dfs(root, 0, 0)
    return ans
```

- **后序写法：每个节点返回「从我出发先往左 / 先往右」的最长长度？** 设 `go_left(node) = 1 + go_right(node.left)`（左孩子存在时），`go_right(node) = 1 + go_left(node.right)`；空孩子方向记 $0$。答案是所有节点两者的最大值。前序是「从上面带下来」，后序是「从下面汇上来」，两种都是 $O(n)$。
