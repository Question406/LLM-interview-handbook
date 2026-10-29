---
id: openai-tree-route-required-tasks
section: openai
order: 928
level: A
title: "OpenAI：从 start 到 end，访问 tree 中所有 task nodes 的最短 route"
quick: "我会把 start、end、tasks 都标成 required。没有通往 required node 的分支可以完全不走。剩下的 subtree 中，start 到 end 路径上的 edges 只走一次，其余分支都必须进去再回来。"
companies:
  - openai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开报告题型改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：OpenAI：从 start 到 end，访问 tree 中所有 task nodes 的最短 route"
    url: "https://aceoffer.app/interviews/oai_shortest_path_in_tree_network_visiting_all_task_nodes"
    type: secondary
---

## 题目描述

来源：AceOffer 公开题面给出 start、end 与 task nodes 的 tree route。下面保留访问要求，并扩展到非负整数 edge weights。

### 输入、接口与规则

实现 `task_route(n, edges, start, end, tasks) -> int`。输入为 n 个 nodes 的合法无向 tree，nodes 编号 0..n-1，edges 的元素为 (u,v,weight)，weight 为非负整数。n≥1，最多 100000。start、end、tasks 中的 nodes 均合法；tasks 可重复或为空。

从 start 出发，访问 tasks 中每个 node 至少一次，最后停在 end。允许重访 nodes 与 edges；返回最小总 edge weight，不要求返回 route，不修改输入。start=end 时仍需完成 tasks。希望时间 `O(N+len(tasks))`，并能处理长链而不依赖 recursion limit。请解释哪些 edges 必须来回走、哪些只需经过一次。

### 输入输出示例

```text
n=5, edges=[(0,1,2),(1,2,3),(1,3,4),(3,4,1)]
start=0, end=2, tasks=[4] -> 返回 15。
可走 0→1→3→4→3→1→2，总 weight=2+4+1+1+4+3。
```

## 回答思路

> **Situation / Task：** Start/end 固定，tasks 必须访问；tree 上任意两点间路径唯一。  
> **Approach / Why：** 保留连接所有 required nodes 的最小 subtree，答案为两倍总 weight 减 start→end distance。  
> **Result / Check：** 用带 visited-task mask 的 shortest-path oracle 验证小 tree。

## 解题思路与参考答案

我会把 start、end、tasks 都标成 required。没有通往 required node 的分支可以完全不走。剩下的 subtree 中，start 到 end 路径上的 edges 只走一次，其余分支都必须进去再回来。

所以答案是 retained subtree 总 weight 的两倍，再减 start 到 end 的 distance。把 tree root 设在 start，反向遍历 nodes 时就能判断每条 parent edge 是否需要保留，不需要真的构造整条 route。

### 完整参考实现

```python
def task_route(n, edges, start, end, tasks):
    graph = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))
    parent = [-1] * n
    distance = [0] * n
    order = [start]
    parent[start] = start
    for u in order:
        for v, w in graph[u]:
            if v == parent[u]:
                continue
            parent[v] = u
            distance[v] = distance[u] + w
            order.append(v)
    required = [False] * n
    for u in [start, end, *tasks]:
        required[u] = True
    total = 0
    for u in reversed(order[1:]):
        if required[u]:
            total += distance[u] - distance[parent[u]]
            required[parent[u]] = True
    return 2 * total - distance[end]
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert task_route(5, [(0, 1, 2), (1, 2, 3), (1, 3, 4), (3, 4, 1)], 0, 2, [4]) == 15
assert task_route(1, [], 0, 0, []) == 0
assert task_route(2, [(0, 1, 0)], 0, 0, [1, 1]) == 0
from heapq import heappush, heappop
from random import Random

rng = Random(12)
for _ in range(100):
    n = 6
    edges = [(i, rng.randrange(i), rng.randrange(5)) for i in range(1, n)]
    g = [[] for _ in range(n)]
    for u, v, w in edges:
        g[u].append((v, w))
        g[v].append((u, w))
    start, end = rng.randrange(n), rng.randrange(n)
    tasks = rng.sample(range(n), 3)
    bit = {u: 1 << i for i, u in enumerate(tasks)}
    full = (1 << len(tasks)) - 1
    heap = [(0, start, bit.get(start, 0))]
    seen = set()
    while heap:
        dist, u, mask = heappop(heap)
        if (u, mask) in seen:
            continue
        seen.add((u, mask))
        if u == end and mask == full:
            break
        for v, w in g[u]:
            heappush(heap, (dist + w, v, mask | bit.get(v, 0)))
    assert task_route(n, edges, start, end, tasks) == dist
print('tree task route tests passed')
```

## 复杂度与追问

时间 `O(N+T)`，空间 `O(N)`，T 为 tasks 输入长度。公式依赖输入是 tree；一般 graph 中任务访问最短 route 不能直接套用。
