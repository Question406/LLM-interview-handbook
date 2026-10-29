---
id: lc-437-path-sum-iii
section: binary-tree-dfs
order: 4
level: S
title: LC 437 · 路径总和 III
quick: >-
  把根到当前节点看成一个数组，用前缀和加哈希计数：答案加上 $cnt[cur - target]$。离开节点时撤销当前前缀和，保证哈希里只有祖先链。时间
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
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 437. Path Sum III
    url: 'https://leetcode.com/problems/path-sum-iii/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定一棵二叉树和目标整数 targetSum，统计节点值之和恰好等于目标的路径条数。路径可以从任意节点开始，在任意节点结束，但每一步都必须从父节点走向一个孩子，不能向上返回或横跨到另一条分支。至少包含一个节点。

### 输入与输出

实现 `pathSum(root: Optional[TreeNode], targetSum: int) -> int`。按不同的起止节点组合分别计数，只返回条数，不返回路径；空树返回 0。示例使用层序列表表示树，实际接收节点对象。

### 约束

- 节点数为 0 到 1000。
- 节点值在 `[-10^9,10^9]`，targetSum 在 `[-1000,1000]`，允许出现负值与零。

### 示例

```text
输入：root = [10,5,-3,3,2,null,11,3,-2,null,1], targetSum = 8
输出：3
```

示例中 `5 -> 3`、`5 -> 2 -> 1` 和 `-3 -> 11` 这三条向下路径的和都是 8。

## 解题思路与参考答案

## 题意

给二叉树和整数 `targetSum`，统计节点值之和等于 `targetSum` 的路径条数。路径不必从根开始、不必在叶子结束，但必须向下（只能从父到子）。节点数 $[0, 1000]$，值在 $[-10^9, 10^9]$，可以为负。

## 思路

我会用前缀和加哈希，因为向下的路径就是根到某节点这条链上的一段连续子数组，和「和为 K 的子数组」是同一个问题。DFS 时维护 `cur`，即根到当前节点的和，哈希 `cnt` 记录祖先链上每个前缀和出现的次数。以当前节点结尾、和为目标的路径数就是 `cnt[cur - target]`。`cnt[0] = 1` 表示空前缀，对应从根开始的路径。

拿第一个测试里的链 10 → 5 → 3、目标 8 来看：走到 3 时 `cur = 18`，表里有前缀和 0、10、15，查 $18-8=10$，命中一次，对应路径 5 → 3。

关键在回溯。进入节点时 `cnt[cur] += 1`，离开时减回去。不减的话，左子树的前缀和会留在表里，右子树拿去配对，算出来的是跨分支的非法路径。

朴素做法是以每个节点为起点再 DFS 一遍，$O(n^2)$；有负数时也没法剪枝，因为后面可能再加回来。

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
    assert (
        pathSum(build_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]), 22) == 3
    )
    assert pathSum(build_tree([]), 0) == 0
    assert pathSum(build_tree([1]), 1) == 1
    assert pathSum(build_tree([0, 0, 0]), 0) == 5
    assert pathSum(build_tree([1, -1, None, 1]), 1) == 3
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert pathSum(build_tree([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1]), 8) == 3
assert pathSum(build_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1]), 22) == 3
assert pathSum(build_tree([]), 0) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，每个节点一次哈希查询和两次更新。额外空间 $O(h)$：哈希里只保留当前祖先链的前缀和，外加递归栈。

## Edge Cases

- 空树返回 $0$。
- 值为 $0$ 或正负抵消时，同一个前缀和会出现多次，所以哈希存次数，用集合会少算。
- 必须先查 `cnt[cur - target]` 再把 `cur` 放进表，否则 `target = 0` 时会把「空路径」算进去。
- 值到 $10^9$，路径和可能超过 32 位；Python 没问题，Java/C++ 要用 `long`。

## 追问

**暴力双重 DFS 怎么写，为什么慢？**
外层遍历每个节点当起点，内层从起点往下累加计数。每个起点最坏扫 $O(n)$ 个后代，总共 $O(n^2)$；平衡树是 $O(n \log n)$。$n \le 1000$ 能过，但面试官想听的是前缀和。

```python
def pathSumBrute(root, targetSum):
    def from_node(node, remain):
        if node is None:
            return 0
        remain -= node.val
        return (
            (remain == 0) + from_node(node.left, remain) + from_node(node.right, remain)
        )

    if root is None:
        return 0
    return (
        from_node(root, targetSum)
        + pathSumBrute(root.left, targetSum)
        + pathSumBrute(root.right, targetSum)
    )
```

**路径必须从根到叶（LC 112 / 113）呢？**
那就不需要前缀和，DFS 带着剩余值往下减，到叶子判断是否为 $0$。要输出路径就维护 `path` 列表，进入时 `append`、离开时 `pop`，命中时拷贝一份。
