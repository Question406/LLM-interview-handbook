---
id: lc-199-binary-tree-right-side-view
section: binary-tree-bfs
order: 1
level: S
title: LC 199 · 二叉树的右视图
quick: >-
  层序 BFS，每层取最后一个节点。从右往左入队则取每层第一个。时间 $O(n)$，额外空间
  $O(w)$。
tags:
  - Tree
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 199. Binary Tree Right Side View
    url: https://leetcode.com/problems/binary-tree-right-side-view/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

从右侧看二叉树，返回每层最右边那个节点的值，自上而下。节点数 $[0, 100]$。

## 思路

标准层序：每轮先记下 `size`，弹出正好一层。该层最后一个就是右视图。

DFS 也可以：先递归右再左，每个深度第一次见到的即右侧。和最大层内元素和（`lc-1161-maximum-level-sum-of-a-binary-tree`）同一骨架，我会优先写 BFS。

只看右孩子链是常见错法：某层右侧缺失时，最右节点可能来自左子树。

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


def rightSideView(root: Optional[TreeNode]) -> List[int]:
    if root is None:
        return []
    q = deque([root])
    ans: List[int] = []
    while q:
        last = 0
        for _ in range(len(q)):
            node = q.popleft()
            last = node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(last)
    return ans


if __name__ == "__main__":
    assert rightSideView(build_tree([1, 2, 3, None, 5, None, 4])) == [1, 3, 4]
    assert rightSideView(build_tree([1, 2, 3, 4, None, None, None, 5])) == [1, 3, 4, 5]
    assert rightSideView(build_tree([1, None, 3])) == [1, 3]
    assert rightSideView(build_tree([])) == []
    assert rightSideView(build_tree([1, 2, None, 3])) == [1, 2, 3]
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(w)$，$w$ 是最宽一层。

## 边界

- 空树：`[]`。
- 只有左链：右侧看不见，但每层最右就是这条链上的节点。
- 某层右孩子缺失：该层最右会落到左侧露出来的节点。

## 追问

- **DFS 怎么写？** 先右后左递归，带深度 `d`；`d == len(ans)` 说明这一层第一次到达，而先右后左保证第一次到达的是最右节点。时间 $O(n)$，额外空间 $O(h)$。

```python
def rightSideViewDFS(root):
    ans = []

    def dfs(node, d):
        if node is None:
            return
        if d == len(ans):
            ans.append(node.val)
        dfs(node.right, d + 1)
        dfs(node.left, d + 1)

    dfs(root, 0)
    return ans
```

- **左视图？** 同一层序骨架，每层取第一个（或先右后左入队则取每层末尾）。DFS 版把递归顺序换成先左后右即可。

```python
from collections import deque

def leftSideView(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        for i in range(len(q)):
            node = q.popleft()
            if i == 0:
                ans.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
    return ans
```
