---
id: lc-1448-count-good-nodes-in-binary-tree
section: binary-tree-dfs
order: 3
level: A
title: LC 1448 · 统计二叉树中好节点的数目
quick: >-
  前序 DFS 带着「根到父节点路径上的最大值」往下传。当前值不小于它就计一个好节点，再用
  $\max$ 更新后传给孩子。时间 $O(n)$，额外空间 $O(h)$。
tags:
  - Tree
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1448. Count Good Nodes in Binary Tree
    url: https://leetcode.com/problems/count-good-nodes-in-binary-tree/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

二叉树中，若从根到节点 $X$ 的路径上没有任何节点的值大于 $X$，则 $X$ 是好节点。返回好节点个数。根一定是好节点。节点数在 $[1, 10^5]$，值在 $[-10^4, 10^4]$。

## 思路

「路径上没有比我大的」等价于「我 $\ge$ 路径上的最大值」。所以只需要往下传一个数 `mx`：根到父节点的最大值。到节点时若 `node.val >= mx` 计数，然后把 `max(mx, node.val)` 传给左右孩子。根调用时传 `-inf` 或根自己的值。

朴素做法是每个节点回头扫整条路径，最坏 $O(n \cdot h)$。前序传参让每条路径的信息只算一次。注意是「不大于」，等于也算好节点。

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


def goodNodes(root: Optional[TreeNode]) -> int:
    def dfs(node: Optional[TreeNode], mx: int) -> int:
        if node is None:
            return 0
        good = 1 if node.val >= mx else 0
        mx = max(mx, node.val)
        return good + dfs(node.left, mx) + dfs(node.right, mx)

    return dfs(root, float("-inf"))


if __name__ == "__main__":
    assert goodNodes(build_tree([3, 1, 4, 3, None, 1, 5])) == 4
    assert goodNodes(build_tree([3, 3, None, 4, 2])) == 3
    assert goodNodes(build_tree([1])) == 1
    assert goodNodes(build_tree([-1, -2, -1])) == 2
    assert goodNodes(build_tree([5, 4, 3, 2, 1])) == 1
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(h)$，链状最坏 $O(n)$。

## 边界

- 只有根：答案 $1$。
- 与路径最大值相等：算好节点，比较用 `>=`。
- 负数值：`mx` 初值用 $-\infty$，不能用 $0$，否则负数根会被漏掉。

## 追问

- **树退化成 $10^5$ 的链，递归爆栈怎么办？** 改显式栈，栈里存 `(node, mx)`，逻辑不变。Python 默认递归上限 $1000$，链状输入必爆，除非调 `sys.setrecursionlimit`。

```python
def goodNodesIter(root):
    if root is None:
        return 0
    ans = 0
    stack = [(root, root.val)]
    while stack:
        node, mx = stack.pop()
        if node.val >= mx:
            ans += 1
        mx = max(mx, node.val)
        if node.left:
            stack.append((node.left, mx))
        if node.right:
            stack.append((node.right, mx))
    return ans
```

- **要求「严格大于路径上所有祖先」？** 比较换成 `node.val > mx`，根要单独算一个（根没有祖先）。只改判断条件，传参方式不变。
