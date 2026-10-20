---
id: lc-124-binary-tree-maximum-path-sum
section: binary-tree
order: 11
level: S
title: LC 124 · 二叉树中的最大路径和
quick: "DFS 向父节点返回单边路径的贡献：$\\max(0,\\text{左},\\text{右})+\\text{根}$。同时用「左贡献 $+$ 右贡献 $+$ 根」更新全局答案，因为完整路径可以在当前节点连接两侧。负贡献不选。时间 $O(n)$，额外空间 $O(h)$。"
tags:
  - Tree
  - DFS
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 124. 二叉树中的最大路径和
    url: https://leetcode.cn/problems/binary-tree-maximum-path-sum/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

路径是树上任意节点到任意节点的无环链（可以不经过根）。返回路径节点值之和的最大值。节点值可负。

## 思路

每个节点做两件事。返回给父节点的是单边：根值加上左右里非负的较大贡献，因为父路径不能同时走左右。对本节点，可以左右都接上，用「左贡献 $+$ 右贡献 $+$ 根」更新全局。

负贡献当 $0$，等于不走那条边。全负时答案是最大的那个节点值。

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


def maxPathSum(root: Optional[TreeNode]) -> int:
    ans = -(10**18)

    def dfs(node: Optional[TreeNode]) -> int:
        nonlocal ans
        if node is None:
            return 0
        left = max(0, dfs(node.left))
        right = max(0, dfs(node.right))
        ans = max(ans, left + right + node.val)
        return node.val + max(left, right)

    dfs(root)
    return ans


if __name__ == "__main__":
    assert maxPathSum(TreeNode(1, TreeNode(2), TreeNode(3))) == 6
    root = TreeNode(-10, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
    assert maxPathSum(root) == 42
    assert maxPathSum(TreeNode(-3)) == -3
    print("ok")
```

## 复杂度

时间 $O(n)$，后序每个节点常数次。额外空间 $O(h)$。

## 边界

- 单节点（含负）：答案就是该值。
- 全负：负边丢弃后全局仍取最大的那个节点，不会拼出更负的路径。
- 最优路径不过根：在某子树内部「左贡献 $+$ 右贡献 $+$ 子根」已经写入全局。

## 追问

- **路径必须从根出发？** 父节点不能同时接左右，所以只保留单边贡献：`node.val + max(0, 左, 右)`。DFS 一遍，全局记这些单边返回值的最大值即可，不要再做 `left+right+val`。空树另行约定。

```python
def maxPathFromRoot(root):
    ans = -(10**18)

    def dfs(node):
        nonlocal ans
        if node is None:
            return 0
        gain = node.val + max(0, dfs(node.left), dfs(node.right))
        ans = max(ans, gain)
        return gain

    dfs(root)
    return ans
```

- **只统计根到叶？** 和 LC 129 同一骨架：往下累加，到叶子才用当前和更新答案；非叶子不结算。节点可负，所以不能半路剪枝。独立卡见 `lc-129-sum-root-to-leaf-numbers`。

```python
def maxRootToLeaf(root):
    ans = -(10**18)

    def dfs(node, acc):
        nonlocal ans
        if node is None:
            return
        acc += node.val
        if node.left is None and node.right is None:
            ans = max(ans, acc)
            return
        dfs(node.left, acc)
        dfs(node.right, acc)

    dfs(root, 0)
    return ans
```
