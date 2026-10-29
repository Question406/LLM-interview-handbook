---
id: lc-399-evaluate-division
section: graph-dfs
order: 4
level: A
title: LC 399 · 除法求值
quick: >-
  把等式建成带权有向图：$a/b=v$ 对应 $a\to b$ 权重 $v$，反向 $b\to a$ 权重 $1/v$。每个查询用 BFS/DFS
  找一条连接两个变量的路径，把沿途权重相乘；不连通或变量不存在返回 $-1$。每个查询 $O(V+E)$。
tags:
  - Graph
  - BFS
  - Union Find
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 399. Evaluate Division
    url: 'https://leetcode.com/problems/evaluate-division/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定一些变量比值等式：equations[i]=[A,B] 和 values[i] 表示 A/B=values[i]。对每个查询 [C,D]，返回由已知等式能够确定的 C/D。若任意一个查询变量从未在已知等式中出现，或者现有等式不足以确定二者比值，则返回 -1.0。

### 输入与输出

实现 `calcEquation(equations, values, queries) -> list[float]`，输出顺序必须与 queries 一致。已知变量除以自身为 1；从未出现的变量即使除以自身也返回 -1.0。

### 约束与约定

- 已知等式与查询各有 1 到 20 条，每一条含两个变量名。
- 变量名长 1 到 5，只含小写英文字母和数字。
- values 与 equations 等长，且 `0 < values[i] <= 20`；输入保证不矛盾，不出现零作除数的情况。

### 示例

```text
输入：equations = [["a","b"],["b","c"]], values = [2.0,3.0], queries = [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]
输出：[6.00000,0.50000,-1.00000,1.00000,-1.00000]
```

示例由 a/b=2 与 b/c=3 得到 a/c=6；变量 e、x 未知，对应查询返回 -1。

[官方原题与完整题面](https://leetcode.com/problems/evaluate-division/description/)。

## 解题思路与参考答案

## 题意

给定若干等式 `equations[i] = [Ai, Bi]` 与值 `values[i]`，表示 $A_i/B_i=$ `values[i]`。对每个查询 `[Cj, Dj]` 求 $C_j/D_j$。变量从未出现、或两点不连通，返回 $-1$。等式之间不矛盾，值都是正数。

## 思路

我把它建成带权图，变量是点，除法是边，查询就是找路径再把权重乘起来。$a/b=v$ 建 $a\to b$ 权 $v$，反向权 $1/v$。查询从 $c$ 走到 $d$，答案是沿途边权的乘积，因为 $a/c = (a/b)\cdot(b/c)$。

拿样例看：$a/b=2$、$b/c=3$，查 $a/c$ 就是从 $a$ 走到 $b$ 再走到 $c$，$2\times 3=6$；查 $b/a$ 走反向边，得 $0.5$；查 $a/e$，图里没有 $e$，返回 $-1$。

等式不矛盾，所以任意一条路径的乘积都一样，BFS 或 DFS 找到就行，用不着最短路。同一个变量比自己是 $1$，前提是它在图里出现过。

并查集也能做，维护每个点到根的乘积，路径压缩时更新权重。白板上我先讲 BFS。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
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
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

建图 $O(E)$。每个查询最坏 $O(V+E)$，总计 $O(Q\cdot(V+E))$，空间 $O(V+E)$。题目里变量和等式都不超过 $20$ 个，这个量级完全够用。

## Edge Cases

查询两端相同但变量从没出现过，比如 `["x", "x"]`，要返回 $-1$。只有变量在图里时 $x/x=1$。

$a/b=v$ 一定要同时建 $b/a=1/v$，漏建反向边，反向查询就会失败。

`bc` 是一个独立的变量名，跟 $b\cdot c$ 没关系。建图时按整个字符串当点，别拆字符。

两个变量都在图里、但不在同一个连通块，BFS 走完都碰不到终点，返回 $-1$。

## 追问

**查询很多时怎么预处理？**
变量很少时可以跑 Floyd：`dist[i][j]` 表示 $i/j$。对角线初始化为 $1$，每条等式写入 $v$ 和 $1/v$，然后两段都已知时令 $\mathrm{dist}[i][j] \leftarrow \mathrm{dist}[i][k]\cdot \mathrm{dist}[k][j]$。预处理 $O(V^3)$，之后每个查询 $O(1)$。

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

**带权并查集怎么写？**
每个点维护 `parent` 和 `weight[x]`，约定 `weight[x] = x / parent(x)`。`find` 做路径压缩时先递归到根，再 `weight[x] *= weight[old_parent]`，这样压缩后仍满足 `weight[x]` 等于 $x/\mathrm{root}$。`union(a,b,v)` 表示 $a/b=v$：根不同就把 $ra$ 挂到 $rb$ 下，权重是 $ra/rb = v\cdot w[b]/w[a]$。查询时根不同或点不存在返回 $-1$，否则 $a/b = w[a]/w[b]$。

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
