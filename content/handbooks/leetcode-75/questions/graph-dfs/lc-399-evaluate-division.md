---
id: lc-399-evaluate-division
section: graph-dfs
order: 4
level: A
title: LC 399 · 除法求值
quick: >-
  把等式转成带权有向图：$a/b=v$ 对应 $a\to b$，权重为 $v$；反向边 $b\to a$ 的权重为 $1/v$。每次查询用 BFS/DFS
  找到连接两个变量的路径，把沿途权重相乘。两点不连通或变量不存在时返回 $-1$。每个查询 $O(V+E)$。
tags:
  - Graph
  - BFS
  - Union Find
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 399. Evaluate Division
    url: https://leetcode.com/problems/evaluate-division/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给定若干等式 `equations[i] = [Ai, Bi]` 与值 `values[i]`，表示 $A_i/B_i=$ `values[i]`。对每个查询 `[Cj, Dj]` 求 $C_j/D_j$。变量从未出现、或两点不连通，返回 $-1$。等式之间不矛盾，值都是正数。

## 思路

把变量当点、除法当带权边。$a/b=v$ 建 $a\to b$ 权 $v$，反向权 $1/v$。查询就是找一条从 $c$ 到 $d$ 的路径，答案是边上权的乘积：$a/c = (a/b)\cdot(b/c)$。等式不矛盾，所以任意一条路径的积都相同，BFS 或 DFS 找到就行，不需要最短路。

同一变量比自己是 $1$（前提是它在图里）。并查集也可：维护到根的乘积，路径压缩时更新权。白板我优先讲 BFS。

## 参考代码

```python
from collections import defaultdict, deque
from typing import Dict, List, Tuple


def calcEquation(
    equations: List[List[str]],
    values: List[float],
    queries: List[List[str]],
) -> List[float]:
    g: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    for (a, b), v in zip(equations, values):
        g[a].append((b, v))
        g[b].append((a, 1.0 / v))

    def bfs(src: str, dst: str) -> float:
        if src not in g or dst not in g:
            return -1.0
        if src == dst:
            return 1.0
        q = deque([(src, 1.0)])
        seen = {src}
        while q:
            x, prod = q.popleft()
            for y, w in g[x]:
                if y in seen:
                    continue
                nxt = prod * w
                if y == dst:
                    return nxt
                seen.add(y)
                q.append((y, nxt))
        return -1.0

    return [bfs(c, d) for c, d in queries]


def close(xs: List[float], ys: List[float]) -> bool:
    return len(xs) == len(ys) and all(abs(x - y) < 1e-9 for x, y in zip(xs, ys))


if __name__ == "__main__":
    ans = calcEquation(
        [["a", "b"], ["b", "c"]],
        [2.0, 3.0],
        [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]],
    )
    assert close(ans, [6.0, 0.5, -1.0, 1.0, -1.0])
    ans = calcEquation(
        [["a", "b"], ["b", "c"], ["bc", "cd"]],
        [1.5, 2.5, 5.0],
        [["a", "c"], ["c", "b"], ["bc", "cd"], ["cd", "bc"]],
    )
    assert close(ans, [3.75, 0.4, 5.0, 0.2])
    ans = calcEquation(
        [["a", "b"]],
        [0.5],
        [["a", "b"], ["b", "a"], ["a", "c"], ["x", "y"]],
    )
    assert close(ans, [0.5, 2.0, -1.0, -1.0])
    ans = calcEquation([["a", "b"], ["c", "d"]], [2.0, 4.0], [["a", "d"], ["d", "c"]])
    assert close(ans, [-1.0, 0.25])
    print("ok")
```

## 复杂度

建图 $O(E)$。每个查询最坏 $O(V+E)$，总计 $O(Q\cdot(V+E))$。空间 $O(V+E)$。题目里变量和等式都不超过 $20$ 个，这个量级完全够。

## 边界

- 查询两端相同但变量从未出现：返回 $-1$，不是 $1$。只有变量在图里时 $x/x=1$。
- 只有一条边的反向：$a/b=v$ 必建 $b/a=1/v$，漏建反向则反向查询失败。
- `bc` 是独立变量名，不是 $b\cdot c$。建图按字符串当点，不要拆字符。
- 两个变量都在图里但不在同一连通块：BFS 走完没碰到终点，返回 $-1$。

## 追问

- **多次查询怎么预处理？** 变量很少时跑 Floyd：`dist[i][j]` 表示 $i/j$ 的积。初始化对角线 $1$，每条等式写入 $v$ 与 $1/v$，然后当两段都已知时令 $\mathrm{dist}[i][j] \leftarrow \mathrm{dist}[i][k]\cdot \mathrm{dist}[k][j]$。之后每个查询 $O(1)$，总预处理 $O(V^3)$。

```python
def calcEquationFloyd(equations, values, queries):
    idx = {}
    for a, b in equations:
        idx.setdefault(a, len(idx))
        idx.setdefault(b, len(idx))
    n = len(idx)
    dist = [[None] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 1.0
    for (a, b), v in zip(equations, values):
        i, j = idx[a], idx[b]
        dist[i][j] = v
        dist[j][i] = 1.0 / v
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] is not None and dist[k][j] is not None:
                    dist[i][j] = dist[i][k] * dist[k][j]
    ans = []
    for c, d in queries:
        if c not in idx or d not in idx or dist[idx[c]][idx[d]] is None:
            ans.append(-1.0)
        else:
            ans.append(dist[idx[c]][idx[d]])
    return ans
```

- **带权并查集？** 每个点维护 `parent` 与 `weight[x]`，约定 `weight[x] = x / parent(x)`。`find` 路径压缩时先递归到根，再 `weight[x] *= weight[old_parent]`，于是压缩后仍满足 $x/\mathrm{root}$。`union(a,b,v)` 表示 $a/b=v$：若根不同，把 $ra$ 挂到 $rb$，权为 $ra/rb = v\cdot w[b]/w[a]$。查询：根不同或点不存在返回 $-1$，否则 $a/b = w[a]/w[b]$。

```python
class WeightedUF:
    def __init__(self):
        self.p, self.w = {}, {}

    def add(self, x):
        if x not in self.p:
            self.p[x] = x
            self.w[x] = 1.0

    def find(self, x):
        if self.p[x] != x:
            orig = self.p[x]
            self.p[x] = self.find(orig)
            self.w[x] *= self.w[orig]
        return self.p[x]

    def union(self, a, b, v):
        self.add(a)
        self.add(b)
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        self.p[ra] = rb
        self.w[ra] = v * self.w[b] / self.w[a]

    def query(self, a, b):
        if a not in self.p or b not in self.p:
            return -1.0
        if self.find(a) != self.find(b):
            return -1.0
        return self.w[a] / self.w[b]
```
