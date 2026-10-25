---
id: lc-1466-reorder-routes-to-make-all-paths-lead-to-the-city-zero
section: graph-dfs
order: 3
level: A
title: LC 1466 · 重新规划路线
quick: "把有向边当无向边建树，原方向记成本 $1$、反向记成本 $0$。从城市 $0$ 往外遍历，走到的每条成本为 $1$ 的边都背离 $0$，必须反转，累加起来就是答案。时间 $O(n)$，额外空间 $O(n)$。"
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

## 题目描述

有编号 0 到 n-1 的 n 个城市与 n-1 条有向道路，`connections[i]=[a,b]` 表示只能从 a 开往 b。忽略方向后，这些道路连接成一棵树。你可以反转某些道路的方向，使每一个城市都能沿有向道路到达城市 0，求最少需要反转多少条。

### 接口与输出

实现 `minReorder(n: int, connections: List[List[int]]) -> int`，返回最小反转数量。目标是所有城市到达 0，不是要求 0 能到达所有城市。

### 合法输入与约束

`2 <= n <= 50000`，connections 恰有 n-1 条道路，每条包含两个不同的合法城市编号。无向结构是一棵树，不包含额外边。

### 示例

```text
输入：n = 6, connections = [[0,1],[1,3],[2,3],[4,0],[4,5]]
输出：3
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/reorder-routes-to-make-all-paths-lead-to-the-city-zero/description/)。

## 解题思路与参考答案

## 题意

$n$ 个城市、$n-1$ 条有向道路 `connections[i] = [a, b]` 表示 $a\to b$，忽略方向后是一棵树。要让每个城市都能开到城市 $0$，最少要反转多少条路的方向。

## 思路

我从城市 $0$ 往外遍历一遍树，数有多少条边现在是背离 $0$ 的。忽略方向后是树，每个城市到 $0$ 的路径唯一，所以每条边最终该朝哪也唯一，必须指向靠近 $0$ 的一侧。

建图时每条 $a\to b$ 存两份：`adj[a]` 里放 `(b, 1)`，`adj[b]` 里放 `(a, 0)`。从 $0$ 出发往外走，沿 `(v, 1)` 走说明原边是从靠近 $0$ 的点指向远离 $0$ 的点，要反转，加 $1$；沿 `(v, 0)` 走说明原边本来就指向 $0$ 这一侧，不用动。

拿 `[[0,1],[1,3],[2,3],[4,0],[4,5]]` 看：从 $0$ 出发，$0\to1$、$1\to3$ 都背离 $0$，各加 1；$3$ 到 $2$ 的原边是 $2\to3$，本来就朝 $0$；$4\to0$ 也朝 $0$；再从 $4$ 走到 $5$，原边 $4\to5$ 背离 $0$，加 1。一共 3。

树上不需要 `seen` 数组，记住父节点、别往回走就行。暴力做法是对每个城市单独找到 $0$ 的路径再统计，$O(n^2)$，没必要。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert minReorder(6, [[0, 1], [1, 3], [2, 3], [4, 0], [4, 5]]) == 3
assert minReorder(5, [[1, 0], [1, 2], [3, 2], [3, 4]]) == 2
assert minReorder(3, [[1, 0], [2, 0]]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，每条边两个方向各看一次。额外空间 $O(n)$，存邻接表和栈。

## 边界

所有边本来就指向 $0$ 时，答案是 $0$。

一条从 $0$ 出发的链 $0\to1\to\cdots$，每条都要反转，答案 $n-1$。

$n$ 最大 $5\times 10^4$，链状树会让递归 DFS 爆栈，所以我用显式栈，BFS 也可以。

## 追问

**反过来，要求 $0$ 能开到所有城市呢？**
答案就是现在指向 $0$ 一侧的边数，也就是 $(n-1)-$ 本题答案。同一次遍历里改成累加 `1 - cost` 就行。

**为什么不用记 `seen`？**
忽略方向后是树，没有环，除了父节点以外的邻居一定没访问过。题目要是改成一般图，就得换成 `seen` 数组，而且「最少反转」也没法再简单地逐边判断了。
