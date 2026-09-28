---
id: lc-1466-reorder-routes-to-make-all-paths-lead-to-the-city-zero
section: graph-dfs
order: 3
level: A
title: LC 1466 · 重新规划路线
quick: >-
  把有向边当无向边建树，原方向记成本 $1$、反向记成本 $0$。从城市 $0$ 往外遍历，走到的每条成本为 $1$
  的边都是背离 $0$ 的，必须反转。时间 $O(n)$，额外空间 $O(n)$。
tags:
  - Graph
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1466. Reorder Routes to Make All Paths Lead to the City Zero
    url: https://leetcode.com/problems/reorder-routes-to-make-all-paths-lead-to-the-city-zero/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

$n$ 个城市、$n-1$ 条有向道路 `connections[i] = [a, b]` 表示 $a\to b$，忽略方向后是一棵树。要让每个城市都能开到城市 $0$，最少要反转多少条路的方向。

## 思路

忽略方向后是树，所以每个城市到 $0$ 的路径唯一，每条边在最终结果里的方向也唯一：必须指向靠近 $0$ 的一侧。问题就变成数一数有多少条边现在是背离 $0$ 的。

建图时每条 $a\to b$ 存两份：`adj[a]` 里放 `(b, 1)`，`adj[b]` 里放 `(a, 0)`。从 $0$ 出发往外走，沿着 `(v, 1)` 走意味着原边方向是「从靠近 $0$ 的点指向远离 $0$ 的点」，要反转，累加 $1$；沿 `(v, 0)` 走说明原边本来就指向 $0$ 这侧，不用动。

树上不需要 `seen` 数组，记父节点防止走回头即可。暴力做法是对每个城市单独找到 $0$ 的路径再统计，$O(n^2)$，没必要。

## 参考代码

```python
from typing import List


def minReorder(n: int, connections: List[List[int]]) -> int:
    adj: List[List[tuple]] = [[] for _ in range(n)]
    for a, b in connections:
        adj[a].append((b, 1))
        adj[b].append((a, 0))
    flips = 0
    stack = [(0, -1)]
    while stack:
        u, parent = stack.pop()
        for v, cost in adj[u]:
            if v != parent:
                flips += cost
                stack.append((v, u))
    return flips


if __name__ == "__main__":
    assert minReorder(6, [[0, 1], [1, 3], [2, 3], [4, 0], [4, 5]]) == 3
    assert minReorder(5, [[1, 0], [1, 2], [3, 2], [3, 4]]) == 2
    assert minReorder(3, [[1, 0], [2, 0]]) == 0
    assert minReorder(2, [[0, 1]]) == 1
    assert minReorder(4, [[0, 1], [1, 2], [2, 3]]) == 3
    print("ok")
```

## 复杂度

时间 $O(n)$，每条边在两个方向各看一次。额外空间 $O(n)$ 存邻接表和栈。

## 边界

- 所有边本来就指向 $0$：答案 $0$。
- 一条从 $0$ 出发的链 $0\to1\to\cdots$：每条都要反转，答案 $n-1$。
- $n$ 最大 $5\times 10^4$，链状树会让递归 DFS 爆栈，我用显式栈；BFS 也可以。

## 追问

- **反过来要求 $0$ 能开到所有城市？** 答案就是现在指向 $0$ 一侧的边数，也就是 $(n-1)-$ 本题答案。同一次遍历累加 `1 - cost` 即可。
- **为什么不用记 `seen`？** 忽略方向后是树，没有环，除了父节点之外的邻居一定没访问过。如果题目改成一般图，就要换成 `seen` 数组，而且「最少反转」不再能简单地逐边判断。
