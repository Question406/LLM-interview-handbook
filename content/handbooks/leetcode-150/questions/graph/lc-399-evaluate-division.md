---
id: lc-399-evaluate-division
section: graph
order: 4
level: A
title: LC 399 · 除法求值
quick: >-
  把变量当点、等式当带权边：$a/b=v$ 就建 $a\to b$ 权 $v$ 和 $b\to a$ 权 $1/v$。每个查询用 BFS/DFS
  找一条路径，把边权乘起来；不连通或变量不存在就返回 $-1$。
tags:
  - Graph
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 399. 除法求值
    url: 'https://leetcode.cn/problems/evaluate-division/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定若干已知的变量比值：`equations[i]=[Ai,Bi]` 与 `values[i]` 共同表示 `Ai / Bi = values[i]`。对每个查询 `[Cj,Dj]`，根据这些已知关系求出 `Cj / Dj`。若关系无法确定，或查询变量从未在任何等式中出现，返回 -1.0。

### 输入与输出

实现 `calcEquation(equations, values, queries) -> List[float]`，结果按查询顺序返回。输入中的变量是非空字符串，数值关系相互一致且没有除零；已知变量除以自身为 1，未知变量即使除以自身也返回 -1。

### 约束

- 等式数和查询数均为 1 到 20，每个等式与查询都恰含两个变量名。
- 变量名长 1 到 5，只含小写英文字母和数字。
- values 与 equations 等长，`0 < values[i] <= 20`；浮点结果按数值容差比较。

### 示例

```text
输入：equations = [["a","b"],["b","c"]], values = [2.0,3.0], queries = [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]
输出：[6.00000,0.50000,-1.00000,1.00000,-1.00000]
```

由 a/b=2 和 b/c=3 可确定 a/c=6；x 从未出现，因此 x/x 的结果仍为 -1。

## 解题思路与参考答案

## 题意

给定若干等式 `equations[i] = [Ai, Bi]` 和值 `values[i]`，表示 $A_i/B_i=$ `values[i]`。对每个查询 `[Cj, Dj]` 求 $C_j/D_j$。变量从没出现过，或者两点不连通，就返回 $-1$。

## 思路

我会把它建成一张带权图，查询就变成找路径。变量是点，$a/b=v$ 建一条 $a\to b$ 权 $v$ 的边，再建反向 $b\to a$ 权 $1/v$。查 $c/d$ 就是找一条 $c\rightsquigarrow d$ 的路径，答案是路径上边权的乘积。

用第一个例子走一遍：$a/b=2$、$b/c=3$，查 $a/c$ 走 $a\to b\to c$，乘起来是 $2\times 3=6$；查 $b/a$ 走反向边，得到 $0.5$；`e` 从没出现过，返回 $-1$。

BFS 和 DFS 都行。点很少，用不着最短路算法，找到一条路径乘出来就是答案。同一个变量比自己是 $1$，前提是它在图里出现过。并查集也能做，维护每个点到根的乘积，路径压缩时更新权重；白板上我优先讲 BFS。

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


if __name__ == "__main__":
    ans = calcEquation(
        [["a", "b"], ["b", "c"]],
        [2.0, 3.0],
        [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]],
    )
    assert ans == [6.0, 0.5, -1.0, 1.0, -1.0]
    ans = calcEquation(
        [["a", "b"], ["b", "c"], ["bc", "cd"]],
        [1.5, 2.5, 5.0],
        [["a", "c"], ["c", "b"], ["bc", "cd"], ["cd", "bc"]],
    )
    assert ans == [3.75, 0.4, 5.0, 0.2]
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
assert ans == [6.0, 0.5, -1.0, 1.0, -1.0]
ans = calcEquation(
    [["a", "b"], ["b", "c"], ["bc", "cd"]],
    [1.5, 2.5, 5.0],
    [["a", "c"], ["c", "b"], ["bc", "cd"], ["cd", "bc"]],
)
assert ans == [3.75, 0.4, 5.0, 0.2]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

建图 $O(E)$，每个查询最坏 $O(V+E)$，空间 $O(V+E)$。这题变量个数很小。

## Edge Cases

查询两端相同、但这个变量从没出现过时，要返回 $-1$，不是 $1$；只有变量在图里时才有 $x/x=1$。每条等式都要把反向边一起建上，$a/b=v$ 必须同时建 $b/a=1/v$，漏了的话反向查询会失败。像 `bc` 这样的名字是一个独立变量，不是 $b\cdot c$，建图时整个字符串当一个点，别拆字符。

## 追问

**查询很多，怎么预处理？**
变量少的时候跑一遍 Floyd，之后每个查询都是 $O(1)$。`dist[i][j]` 表示 $i/j$ 的积，对角线初始化成 $1$，每条等式写入 $v$ 和 $1/v$，然后在两段都已知时更新

$$
\mathrm{dist}[i][j] \leftarrow \mathrm{dist}[i][k]\cdot \mathrm{dist}[k][j]
$$

总预处理是 $O(V^3)$。

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
每个点维护 `parent` 和 `weight[x]`，约定 `weight[x] = x / parent(x)`。`find` 做路径压缩时先递归到根，再 `weight[x] *= weight[old_parent]`，压缩完仍然表示 $x/\mathrm{root}$。`union(a,b,v)` 表示 $a/b=v$，如果两个根不同，就把 $ra$ 挂到 $rb$ 下面，权重是

$$
\frac{ra}{rb} = v\cdot \frac{w[b]}{w[a]}.
$$

查询时点不存在或者根不同就返回 $-1$，否则 $a/b = w[a]/w[b]$。

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
