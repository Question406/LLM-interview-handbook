---
id: lc-437-path-sum-iii
section: binary-tree-dfs
order: 4
level: S
title: LC 437 · 路径总和 III
quick: >-
  把根到当前节点看成一条数组，用前缀和 + 哈希计数：答案加上 $cnt[cur - target]$。回溯时撤销当前前缀和，保证哈希里只有祖先链。时间
  $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Prefix Sum
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 437. Path Sum III
    url: https://leetcode.com/problems/path-sum-iii/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给二叉树和整数 `targetSum`，统计节点值之和等于 `targetSum` 的路径条数。路径不必从根开始、不必在叶子结束，但必须向下（只能从父到子）。节点数 $[0, 1000]$，值在 $[-10^9, 10^9]$，可以为负。

## 思路

向下的路径就是根到某节点这条链上的一段连续子数组，和「和为 K 的子数组」一样用前缀和。DFS 时维护 `cur` = 根到当前节点的和，哈希 `cnt` 记录祖先链上每个前缀和出现的次数。以当前节点结尾、和为目标的路径数就是 `cnt[cur - target]`。`cnt[0] = 1` 表示空前缀，对应从根开始的路径。

关键是回溯：进入节点时 `cnt[cur] += 1`，离开时减回去。不减的话，左子树的前缀和会留在表里，右子树拿去配对，算出的是跨分支的非法路径。朴素做法是以每个节点为起点再 DFS 一遍，$O(n^2)$；有负数时也不能剪枝，因为后面可能再加回来。

## 参考代码

```python
from __future__ import annotations

from collections import defaultdict, deque
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


def pathSum(root: Optional[TreeNode], targetSum: int) -> int:
    cnt = defaultdict(int)
    cnt[0] = 1

    def dfs(node: Optional[TreeNode], cur: int) -> int:
        if node is None:
            return 0
        cur += node.val
        res = cnt[cur - targetSum]
        cnt[cur] += 1
        res += dfs(node.left, cur) + dfs(node.right, cur)
        cnt[cur] -= 1
        return res

    return dfs(root, 0)


if __name__ == "__main__":
    assert pathSum(build_tree([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1]), 8) == 3
    assert pathSum(build_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]), 22) == 3
    assert pathSum(build_tree([]), 0) == 0
    assert pathSum(build_tree([1]), 1) == 1
    assert pathSum(build_tree([0, 0, 0]), 0) == 5
    assert pathSum(build_tree([1, -1, None, 1]), 1) == 3
    print("ok")
```

## 复杂度

时间 $O(n)$，每个节点一次哈希查询和两次更新。额外空间 $O(h)$：哈希里只保留当前祖先链的前缀和，外加递归栈。

## 边界

- 空树：返回 $0$。
- 值为 $0$ 或正负抵消：同一个前缀和会出现多次，所以哈希存次数，不能用集合。
- 必须先查 `cnt[cur - target]` 再把 `cur` 放进表：否则 `target = 0` 时会把「空路径」算进去。
- 值到 $10^9$，路径和可能超 32 位；Python 没问题，Java/C++ 要用 `long`。

## 追问

- **暴力双重 DFS 怎么写，为什么慢？** 外层遍历每个节点当起点，内层从起点往下累加计数。每个起点最坏扫 $O(n)$ 个后代，总 $O(n^2)$；平衡树是 $O(n \log n)$。$n \le 1000$ 能过，但面试官想听前缀和。

```python
def pathSumBrute(root, targetSum):
    def from_node(node, remain):
        if node is None:
            return 0
        remain -= node.val
        return (remain == 0) + from_node(node.left, remain) + from_node(node.right, remain)

    if root is None:
        return 0
    return from_node(root, targetSum) + pathSumBrute(root.left, targetSum) + pathSumBrute(root.right, targetSum)
```

- **路径必须从根到叶（LC 112 / 113）？** 不需要前缀和，DFS 带剩余值往下减，到叶子判断是否为 $0$。要输出路径就维护 `path` 列表，进入 `append`、离开 `pop`，命中时拷贝一份。
