---
id: p3a-microsoft-dna-shotgun-sequencing
section: microsoft
order: 600
level: A
title: "Microsoft AI / Copilot：DNA fragments：有向链、欧拉路径与多链"
quick: "把 DNA 片段看成有向边、片段两端的标签看成顶点，单链恢复就是找一条欧拉路径：先检查出入度条件，再用 Hierholzer 算法走完所有边，最后用长度检查排除不连通的情况。"
companies:
  - microsoft
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Microsoft AI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Microsoft AI / Copilot · dna-shotgun-sequencing"
    url: https://www.1point3acres.com/interview/problems/company/microsoft/dna-shotgun-sequencing
    type: secondary
---

## 题目

每个 DNA 片段用起始标签和结束标签表示，要求把所有片段首尾相接，恢复出原来的序列。之后再逐步扩展到无向片段和多条链的版本。

> 来源：一亩三分地 Microsoft 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

把片段看成边、端点标签看成顶点。「每个片段恰好用一次、首尾相接」正好是图上的欧拉路径，不是普通的点遍历：同一个标签可以经过多次，但每条边只能用一次，两条一样的片段（平行边）也要各用一次。

有向图存在欧拉路径的条件：

- 除了起点和终点，每个点的出度等于入度；
- 最多有一个点出度比入度多 1（起点），一个点入度比出度多 1（终点），或者所有点都平衡（路径首尾相同）；
- 所有边在同一个连通部分里。

满足度数条件后，用 Hierholzer 算法：从起点沿着没用过的边一直走，走到没有出边的点就把它出栈加到结果里，最后把结果反转。度数条件不保证连通，所以最后还要检查结果长度是不是边数加 1。

多链版本怎么拆，要以面试官给的具体约束为准，比如要不要链数最少。不能为了得到一条链，把本来不相接的片段硬拼在一起。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `euler_chain(edges)`：`edges` 是 `(start_tag, end_tag)` 有向边列表，标签是字符串，允许平行边。返回恰好用每条边一次的标签序列；不存在这样的单链时返回 `None`；空输入返回 `[]`。
- `chains(edges)`：把任意边集拆成若干条有向链，每条边恰好用一次。这是手册约定的多链练习，不保证链数最少。
- 最多 $10^5$ 条边。只处理标签，不拼接片段里实际的碱基序列。

### 输入输出示例

```text
euler_chain([("a", "b"), ("b", "a"), ("a", "c")])  -> ["a", "b", "a", "c"]
euler_chain([("a", "b"), ("c", "d")])              -> None
chains([("a", "b"), ("c", "d")])                   -> [["a", "b"], ["c", "d"]]
```

第二个例子的两个片段接不上，没有单链，但可以拆成两条链。

### 解题思路与正确性

`euler_chain` 先统计出入度，检查上面的度数条件；起点取出度多 1 的那个点，所有点都平衡时取任意一个有出边的点（这里取字典序最小的，结果更稳定）。

Hierholzer 用一个栈：栈顶还有没用的出边就沿边走，并把这条边从邻接表里删掉；没有出边就把栈顶弹出加入路线。每条边恰好被删一次，所以路线里每条边恰好用一次。反转后就是从起点出发的顺序。

如果有边落在另一个连通分量里，从起点永远走不到它们，路线长度会小于边数加 1，这时返回 `None`。比如 `a ⇄ b` 和 `c ⇄ d` 两个环，度数都平衡，靠长度检查才能发现。

`chains` 是贪心：从每个还有出边的点出发，沿着没用过的边走到底，得到一条链，重复直到所有边用完。每条边被删一次，所以覆盖恰好一次，但链数不一定最少。

### 完整参考实现（Python 3）

```python
from collections import Counter, defaultdict


def build_adjacency(edges):
    adjacency = defaultdict(list)  # 标签 -> 还没用过的出边终点；平行边重复出现
    for start_tag, end_tag in edges:
        adjacency[start_tag].append(end_tag)
    return adjacency


def euler_chain(edges):
    """返回恰好用每条有向边一次的标签序列；不存在这样的单链时返回 None。"""
    if not edges:
        return []
    adjacency = build_adjacency(edges)
    out_degree = Counter(start_tag for start_tag, _ in edges)
    in_degree = Counter(end_tag for _, end_tag in edges)
    nodes = set(out_degree) | set(in_degree)

    # 度数条件：其余点出入度相等，最多一个起点「出度多 1」、一个终点「入度多 1」
    if any(abs(out_degree[node] - in_degree[node]) > 1 for node in nodes):
        return None
    starts = [node for node in nodes if out_degree[node] - in_degree[node] == 1]
    ends = [node for node in nodes if in_degree[node] - out_degree[node] == 1]
    if (len(starts), len(ends)) not in ((0, 0), (1, 1)):
        return None
    start = starts[0] if starts else min(node for node in nodes if out_degree[node])

    # Hierholzer：沿未用的边一直走，走不动的点出栈加入路线，最后反转
    stack = [start]
    route = []
    while stack:
        node = stack[-1]
        if adjacency[node]:
            stack.append(adjacency[node].pop())
        else:
            route.append(stack.pop())
    route.reverse()

    # 度数条件不检查连通性：如果有边在别的连通分量里，路线会比边数 + 1 短
    if len(route) != len(edges) + 1:
        return None
    return route


def chains(edges):
    """把边集拆成若干条有向链（trail），每条边恰好用一次；不保证链数最少。"""
    adjacency = build_adjacency(edges)
    result = []
    for start in sorted(adjacency):
        while adjacency[start]:
            path = [start]
            node = start
            while adjacency[node]:
                node = adjacency[node].pop()
                path.append(node)
            result.append(path)
    return result
```

### 可执行测试

```python
def used_edges(paths):
    return Counter(pair for path in paths for pair in zip(path, path[1:]))

# 单链：a -> b -> a -> c，每条边恰好用一次
edges = [("a", "b"), ("b", "a"), ("a", "c")]
route = euler_chain(edges)
assert Counter(zip(route, route[1:])) == Counter(edges)
assert route[0] == "a"
assert route[-1] == "c"

# 空输入返回空序列
assert euler_chain([]) == []

# 两个不连通的片段：度数条件不满足，无单链
assert euler_chain([("a", "b"), ("c", "d")]) is None

# 度数平衡但不连通：靠长度检查发现
assert euler_chain([("a", "b"), ("b", "a"), ("c", "d"), ("d", "c")]) is None

# 多链：每条边恰好用一次，包括平行边
for case in ([], [("a", "b"), ("a", "b"), ("b", "a")], [("a", "b"), ("c", "d")]):
    assert used_edges(chains(case)) == Counter(case)
```

### 复杂度与追问

设边数为 E、标签数为 V。`euler_chain` 是 O(E + V) 时间；`chains` 要对顶点排序，是 O(V log V + E)。两者空间都是 O(E + V)。

- 无向片段怎么做？每个片段可以正着接也可以反着接，要在两个端点的邻接表里都放这条边，并带上同一个边编号。走过一次就按编号标记已用，另一端的那份也要跳过。不能简单地把一个无向片段当成两条有向片段，否则同一个片段会被用两次。无向图欧拉路径的条件也变了：奇数度的点必须是 0 个或 2 个。
- 要求链数最少怎么办？在有向图的每个连通分量里，最少链数等于 $\max(1, \sum_v \max(0, \text{out}(v) - \text{in}(v)))$。可以先把多余的出度和入度用虚拟边配对连起来，跑一次欧拉路径，再在虚拟边处断开。
