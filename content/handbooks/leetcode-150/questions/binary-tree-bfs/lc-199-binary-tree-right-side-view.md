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
updatedAt: 2026-08-21
sources:
  - title: 199. 二叉树的右视图
    url: https://leetcode.cn/problems/binary-tree-right-side-view/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

从右侧看二叉树，返回每层最右边那个节点的值，自上而下。

## 思路

标准层序：每轮先记下 `size`，弹出正好一层。该层最后一个就是右视图。

DFS 也可以：先递归右再左，每个深度第一次见到的即右侧。和 102 / 103 同一骨架，我会优先写 BFS。

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
    root = TreeNode(1, TreeNode(2, None, TreeNode(5)), TreeNode(3, None, TreeNode(4)))
    assert rightSideView(root) == [1, 3, 4]
    only_left = TreeNode(1, TreeNode(2, TreeNode(3)))
    assert rightSideView(only_left) == [1, 2, 3]
    assert rightSideView(None) == []
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(w)$，$w$ 是最宽一层。

## 边界

- 空树：`[]`。
- 只有左链：右侧看不见，但每层最右就是这条链上的节点。
- 某层右孩子缺失：该层最右会落到左侧露出来的节点。

## 追问

- **左视图？** 同一层序骨架，每层取第一个（或先右后左入队则取每层末尾）。DFS：先左后右，每个深度第一次见到的即左侧。时间 $O(n)$。

```python
from collections import deque

def leftSideView(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        first = None
        for i in range(len(q)):
            node = q.popleft()
            if i == 0:
                first = node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(first)
    return ans
```

- **锯齿 / 层均值？** 切层 BFS 骨架不变，只换层内收集。锯齿：已有奇数层则当前层 `reverse`（或双端 `appendleft`），独立卡见 `lc-103-binary-tree-zigzag-level-order-traversal`。均值：求和再除以本层个数，独立卡见 `lc-637-average-of-levels-in-binary-tree`。右视图是「每层最后一个」，这三题常串着考。

```python
from collections import deque

def zigzagLevelOrder(root):
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
        if len(ans) % 2 == 1:
            level.reverse()
        ans.append(level)
    return ans


def averageOfLevels(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        total, size = 0, len(q)
        for _ in range(size):
            node = q.popleft()
            total += node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(total / size)
    return ans
```
