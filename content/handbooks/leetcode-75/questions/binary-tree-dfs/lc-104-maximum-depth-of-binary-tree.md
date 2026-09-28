---
id: lc-104-maximum-depth-of-binary-tree
section: binary-tree-dfs
order: 1
level: S
title: LC 104 · 二叉树的最大深度
quick: >-
  空树深度 $0$。否则 $1+\max(\text{左深},\text{右深})$，DFS 或层序均可。时间 $O(n)$，额外空间
  $O(h)$。
tags:
  - Tree
  - DFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 104. Maximum Depth of Binary Tree
    url: https://leetcode.com/problems/maximum-depth-of-binary-tree/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给定二叉树根节点，返回最大深度：根到最远叶的节点个数。空树为 $0$。

## 思路

后序 DFS：先求左右子树深度，当前深度是 $1$ 加上较大者。空节点返回 $0$，叶节点返回 $1$。

层序 BFS 数层数也能做。递归先写，再补一句栈深最坏 $O(n)$。

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


def maxDepth(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    return 1 + max(maxDepth(root.left), maxDepth(root.right))


if __name__ == "__main__":
    assert maxDepth(build_tree([3, 9, 20, None, None, 15, 7])) == 3
    assert maxDepth(build_tree([1, None, 2])) == 2
    assert maxDepth(build_tree([])) == 0
    assert maxDepth(build_tree([1])) == 1
    assert maxDepth(build_tree([1, 2, None, 3, None, 4])) == 4
    print("ok")
```

## 复杂度

时间 $O(n)$，每个节点一次。额外空间 $O(h)$，$h$ 是树高，最坏链状 $O(n)$。

## 边界

- 空树：深度 $0$。
- $n=1$：只有根，深度 $1$。
- 只有左链或只有右链：深度等于节点数。

## 追问

- **改成最小深度（LC 111）？** 不能把 $\max$ 直接换成 $\min$。空孩子返回 $0$，单侧树 `min(左, 0)+1` 会得到 $1$，把缺失的那边当成叶子了。最小深度是根到最近叶子的节点数：若只有一侧孩子，必须走进那一侧；两侧都有才取较小。BFS 第一次碰到叶子就是答案，偏斜树往往比 DFS 早停。

```python
from collections import deque

def minDepth(root):
    if root is None:
        return 0
    q = deque([(root, 1)])
    while q:
        node, d = q.popleft()
        if node.left is None and node.right is None:
            return d
        if node.left:
            q.append((node.left, d + 1))
        if node.right:
            q.append((node.right, d + 1))
```

- **迭代求最大深度？** DFS 用栈存 `(node, depth)`，弹出时用当前深度更新答案，左右孩子 `depth+1` 入栈。或 BFS 按层切：每过一层 `ans += 1`，队列掏空即最大深度。时间都 $O(n)$；BFS 额外空间 $O(w)$，链状时栈/递归 $O(n)$。

```python
def maxDepthIter(root):
    ans = 0
    stack = [(root, 1)] if root else []
    while stack:
        node, d = stack.pop()
        ans = max(ans, d)
        if node.left:
            stack.append((node.left, d + 1))
        if node.right:
            stack.append((node.right, d + 1))
    return ans
```
