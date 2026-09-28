---
id: ali-algo-level-order
section: alibaba-oa
order: 35
level: B
title: 阿里手撕：二叉树层序及变形要准备哪些？
quick: >-
  我会用队列 BFS，每层先 `size=q.size()` 再吐正好一层。锯齿、右侧视图、层均值都是同一骨架，只换收集方式。
tags:
  - Alibaba
  - BFS
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 二叉树的层序遍历
    url: https://leetcode.cn/problems/binary-tree-level-order-traversal/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题 / 考点说明

- 对应：LeetCode 102 及 103 / 199 变形

层序要按层切开。不要把整棵树丢进一个 list 再事后切层。空根返回空。锯齿、右侧视图、层均值都是同一骨架，只换收集方式。

## 思路

队列里先放根。每一轮开始记下 `size=len(q)`，只弹出这么多个，正好一层。弹出时把左右孩子入队。

- 102：每层 append 一个 list。
- 103：偶数层再反转，或该层用双端队列头插/尾插。
- 199：每层最后一个（或从右往左 BFS 的第一个）就是右视图。

追问多叉树 / 图：骨架仍是 BFS；图必须 `visited`，否则有环会死循环。连通块计数就是岛屿。

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


def level_order(root: Optional[TreeNode]) -> List[List[int]]:
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


def zigzag_level_order(root: Optional[TreeNode]) -> List[List[int]]:
    levels = level_order(root)
    for i, level in enumerate(levels):
        if i % 2 == 1:
            level.reverse()
    return levels


def right_side_view(root: Optional[TreeNode]) -> List[int]:
    return [level[-1] for level in level_order(root)]


if __name__ == "__main__":
    #     3
    #    / \
    #   9  20
    #     /  \
    #    15   7
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert level_order(root) == [[3], [9, 20], [15, 7]]
    assert zigzag_level_order(root) == [[3], [20, 9], [15, 7]]
    assert right_side_view(root) == [3, 20, 7]
    assert level_order(None) == []
    print("ok")
```

## 复杂度

时间 $O(n)$，空间 $O(w)$，$w$ 是最宽一层（最坏 $O(n)$）。DFS 按深度塞桶能过题，但层序我先给 BFS。

## 边界与追问

1. 空树、只有左链、完全二叉树最底层最宽：切层用当轮 `size`，不要用 `while q` 一次掏光。
2. 追问锯齿 / 右视图 / 层均值：同一骨架，换收集；锯齿层内反转即可。
3. 追问图或多叉树：层序就是 BFS，图要 `visited`；连通块计数按岛屿思路。
