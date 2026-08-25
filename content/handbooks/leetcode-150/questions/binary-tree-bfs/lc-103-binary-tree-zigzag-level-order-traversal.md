---
id: lc-103-binary-tree-zigzag-level-order-traversal
section: binary-tree-bfs
order: 4
level: A
title: LC 103 · 二叉树的锯齿形层序遍历
quick: >-
  先做普通层序，从 $1$ 数的偶数层再反转（根层从左到右）。或该层用双端队列头插 / 尾插。时间 $O(n)$，额外空间
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
  - title: 103. 二叉树的锯齿形层序遍历
    url: https://leetcode.cn/problems/binary-tree-zigzag-level-order-traversal/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

层序遍历，但方向交替：第 $0$ 层从左到右，第 $1$ 层从右到左，再交替。

## 思路

先按 LC 102 切层。从 $1$ 数的偶数层（根是第 $1$ 层、从左到右）再 `reverse`。入队顺序始终左再右，不要在队列里来回改方向。

也可用双端队列：奇数层尾插，偶数层头插。白板我说「偶数层反转」时，会先确认层号从 $1$ 计。

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


def zigzagLevelOrder(root: Optional[TreeNode]) -> List[List[int]]:
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
        if len(ans) % 2 == 1:
            level.reverse()
        ans.append(level)
    return ans


if __name__ == "__main__":
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert zigzagLevelOrder(root) == [[3], [20, 9], [15, 7]]
    assert zigzagLevelOrder(TreeNode(1)) == [[1]]
    assert zigzagLevelOrder(None) == []
    print("ok")
```

## 复杂度

时间 $O(n)$，反转一层仍线性。额外空间 $O(w)$。

## 边界

- 空树：`[]`。
- 只有一层：无需反转。
- 该反转的那一层只有一个节点：反转无感。

## 追问

- **层号从 $1$ 计还是从 $0$ 计？** 先对齐。题面第 $0$ 层（根）从左到右，第 $1$ 层从右到左。若口头说「奇数层左到右」，那是 $1$-indexed。代码里用 `len(ans)` 的奇偶最稳：已有奇数层时当前这层要反。这块容易和入队顺序搞反。

- **层内双端插入、不事后 `reverse`？** 队列仍左孩子再右孩子。当前层用 `deque`：从左到右就 `append`，从右到左就 `appendleft`。指针版「之字」打印同理，先切层再决定头插还是尾插。时间仍 $O(n)$。

```python
from collections import deque

def zigzagLevelOrder(root):
    if root is None:
        return []
    q, ans, l2r = deque([root]), [], True
    while q:
        level = deque()
        for _ in range(len(q)):
            node = q.popleft()
            if l2r:
                level.append(node.val)
            else:
                level.appendleft(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(list(level))
        l2r = not l2r
    return ans
```
