---
id: lc-129-sum-root-to-leaf-numbers
section: binary-tree
order: 10
level: A
title: LC 129 · 求根节点到叶节点数字之和
quick: >-
  DFS 带前缀：到下一层 `acc = acc * 10 + val`，叶子把 `acc` 加入答案。时间 $O(n)$，额外空间
  $O(h)$。
tags:
  - Tree
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 129. 求根节点到叶节点数字之和
    url: https://leetcode.cn/problems/sum-root-to-leaf-numbers/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

根到叶的每条路径表示一个十进制数（节点值是 $0$ 到 $9$）。返回所有这些数的和。

## 思路

深度优先带当前前缀。进入节点先 `acc = acc * 10 + node.val`。若是叶子，把 `acc` 加进总和；否则继续左右。

和 LC 112 同一骨架，这里收集的是路径数字。空树和为 $0$。

## 参考代码

```python
from __future__ import annotations

from typing import Optional


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


def sumNumbers(root: Optional[TreeNode]) -> int:
    def dfs(node: Optional[TreeNode], acc: int) -> int:
        if node is None:
            return 0
        acc = acc * 10 + node.val
        if node.left is None and node.right is None:
            return acc
        return dfs(node.left, acc) + dfs(node.right, acc)

    return dfs(root, 0)


if __name__ == "__main__":
    assert sumNumbers(TreeNode(1, TreeNode(2), TreeNode(3))) == 25
    root = TreeNode(4, TreeNode(9, TreeNode(5), TreeNode(1)), TreeNode(0))
    assert sumNumbers(root) == 1026
    assert sumNumbers(None) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(h)$。路径长度受题面约束，`acc` 用 `int` 即可。

## 边界

- 单节点：答案就是该位数字。
- 含 $0$：前缀乘十再加 $0$ 仍合法，例如 $10$。
- 只有一侧孩子：另一侧不要把当前 `acc` 当叶子加进去。

## 追问

- **路径用链表 / 数组存每一位？** 能做，但从叶往回乘 $10^k$ 要先知道深度，或额外数组再 `int(''.join(...))`。DFS 带 `acc = acc * 10 + val` 已经是同一信息，少一次拼装。回溯若改 `acc` 引用才需要还原；本题 `acc` 按值传递，回上一层自然旧值。

- **二进制路径和（LC 1022）？** 每位是 $0/1$，把十进制的 $10$ 换成 $2$：`acc = (acc << 1) | node.val`，叶子把 `acc` 加入总和。其余骨架不变。时间 $O(n)$。

```python
def sumRootToLeaf(root):
    def dfs(node, acc):
        if node is None:
            return 0
        acc = (acc << 1) | node.val
        if node.left is None and node.right is None:
            return acc
        return dfs(node.left, acc) + dfs(node.right, acc)

    return dfs(root, 0)
```
