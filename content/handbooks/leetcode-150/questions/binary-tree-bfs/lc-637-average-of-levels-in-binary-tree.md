---
id: lc-637-average-of-levels-in-binary-tree
section: binary-tree-bfs
order: 2
level: A
title: LC 637 · 二叉树的层平均值
quick: >-
  层序切层，每层求和除以个数。注意用浮点。时间 $O(n)$，额外空间
  $O(w)$。
tags:
  - Tree
  - BFS
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 637. 二叉树的层平均值
    url: https://leetcode.cn/problems/average-of-levels-in-binary-tree/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

返回二叉树每一层节点值的平均值，自上而下，用浮点数。

## 思路

队列 BFS，每轮 `size=len(q)` 只处理一层。累加该层和，除以 `size` 写入答案。

DFS 按深度塞桶再平均也能做。和右视图同一骨架，切层 BFS 先写。

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


def averageOfLevels(root: Optional[TreeNode]) -> List[float]:
    if root is None:
        return []
    q = deque([root])
    ans: List[float] = []
    while q:
        total = 0
        size = len(q)
        for _ in range(size):
            node = q.popleft()
            total += node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(total / size)
    return ans


if __name__ == "__main__":
    root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert averageOfLevels(root) == [3.0, 14.5, 11.0]
    assert averageOfLevels(TreeNode(1)) == [1.0]
    assert averageOfLevels(None) == []
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(w)$。Python 的 `int` 不会溢出；其他语言用 `long` 再除。

## 边界

- 空树：`[]`。
- 单节点：`[root.val]` 的浮点。
- 一层只有一个很大的数：Python `int` 安全；其他语言先用 `long` 再除。

## 追问

- **只要层和、不要均值？** 去掉除法，每层累加写入答案。骨架仍是 `size=len(q)` 切层。注意求和溢出；均值那题除以 `size` 才得到浮点。

```python
from collections import deque

def levelSums(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        total = 0
        for _ in range(len(q)):
            node = q.popleft()
            total += node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(total)
    return ans
```

- **每层中位数？** 不能只累加。层内先收集再排序，取中位（偶数层两条平均，看题面）。或层内维护两个堆（对顶堆）在线求中位，单层 $O(w\log w)$，整体 $O(n\log w)$。切层 BFS 仍负责「谁和谁一层」。

```python
from collections import deque

def medianOfLevels(root):
    if root is None:
        return []
    q, ans = deque([root]), []
    while q:
        vals = []
        for _ in range(len(q)):
            node = q.popleft()
            vals.append(node.val)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        vals.sort()
        m = len(vals)
        ans.append(vals[m // 2] if m % 2 else (vals[m // 2 - 1] + vals[m // 2]) / 2)
    return ans
```
