---
id: lc-1161-maximum-level-sum-of-a-binary-tree
section: binary-tree-bfs
order: 2
level: A
title: LC 1161 · 最大层内元素和
quick: >-
  层序 BFS 逐层求和，严格大于当前最优才更新层号，这样并列时保留最小层号。最优初值用
  $-\infty$，因为值可以为负。时间 $O(n)$，额外空间 $O(w)$。
tags:
  - Tree
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1161. Maximum Level Sum of a Binary Tree
    url: https://leetcode.com/problems/maximum-level-sum-of-a-binary-tree/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

根在第 $1$ 层，孩子在第 $2$ 层，依此类推。返回层内节点值之和最大的那一层的层号；多个层并列最大时返回最小的层号。节点数 $[1, 10^4]$，值在 $[-10^5, 10^5]$。

## 思路

按层切的 BFS：每轮用 `len(q)` 固定这一层的节点数，弹出时累加，同时把孩子入队。一层结束后和 `best` 比较，严格大于才更新 `best` 和 `ans`。从上往下扫，用 `>` 就天然保留了并列里最小的层号，写成 `>=` 会返回最深的那层。

`best` 初值必须是 $-\infty$。全负数的树里每层和都小于 $0$，初值写 $0$ 就一次都不会更新，最后返回 $0$，不是合法层号。DFS 也能做，按深度把和累加进数组，最后取最大值的第一个下标。

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


def maxLevelSum(root: Optional[TreeNode]) -> int:
    best, ans, level = float("-inf"), 0, 0
    q = deque([root]) if root else deque()
    while q:
        level += 1
        total = 0
        for _ in range(len(q)):
            node = q.popleft()
            total += node.val
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        if total > best:
            best, ans = total, level
    return ans


if __name__ == "__main__":
    assert maxLevelSum(build_tree([1, 7, 0, 7, -8, None, None])) == 2
    assert maxLevelSum(build_tree([989, None, 10250, 98693, -89388, None, None, None, -32127])) == 2
    assert maxLevelSum(build_tree([5])) == 1
    assert maxLevelSum(build_tree([-5, -1, -2])) == 2
    assert maxLevelSum(build_tree([1, 1, 0])) == 1
    print("ok")
```

## 复杂度

时间 $O(n)$。额外空间 $O(w)$，$w$ 是最宽一层。

## 边界

- 只有根：返回 $1$。
- 全负数：`best` 初值 $-\infty$，否则判断失效。
- 多层并列最大：用严格大于，返回最小层号。

## 追问

- **DFS 写法？** 递归带深度，`sums[d] += val`，深度第一次到达时 `append`。最后取最大值第一次出现的下标加 $1$。时间 $O(n)$，额外空间 $O(h)$ 加上层数。

```python
def maxLevelSumDFS(root):
    sums = []

    def dfs(node, d):
        if node is None:
            return
        if d == len(sums):
            sums.append(0)
        sums[d] += node.val
        dfs(node.left, d + 1)
        dfs(node.right, d + 1)

    dfs(root, 0)
    return sums.index(max(sums)) + 1
```

- **改成返回每层的最大值（LC 515）或右视图？** 切层骨架完全一样，只换层内聚合：取最大值就用 `max`，右视图取每层最后一个，见 `lc-199-binary-tree-right-side-view`。
