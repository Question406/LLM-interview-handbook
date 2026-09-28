---
id: lc-133-clone-graph
section: graph
order: 3
level: A
title: LC 133 · 克隆图
quick: >-
  节点是 `val` + `neighbors`。哈希「旧节点 $\to$ 新节点」，DFS/BFS
  克隆邻居；已建过的直接复用，才能处理环。
tags:
  - Graph
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 133. 克隆图
    url: https://leetcode.cn/problems/clone-graph/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

无向连通图。每个节点有整数值 `val` 和邻居列表 `neighbors`。返回图的深拷贝：新节点值相同，邻接关系相同，但对象全是新的。空图返回空。

## 思路

图里有环，不能只按树递归。维护哈希：旧节点 $\to$ 已克隆的新节点。DFS：若当前旧节点已在表里，直接返回对应新节点；否则先 `new Node(val)` 登记，再递归克隆邻居填进 `neighbors`。先登记再递归，避免环上死循环。

BFS 同样：队列扩邻接，哈希保证每个旧节点只建一次。开口：先放入哈希再走邻居。

## 参考代码

```python
from typing import List, Optional


class Node:
    def __init__(self, val: int = 0, neighbors: Optional[List["Node"]] = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def cloneGraph(node: Optional[Node]) -> Optional[Node]:
    if node is None:
        return None
    mp = {}

    def dfs(cur: Node) -> Node:
        if cur in mp:
            return mp[cur]
        copy = Node(cur.val)
        mp[cur] = copy
        copy.neighbors = [dfs(nb) for nb in cur.neighbors]
        return copy

    return dfs(node)


if __name__ == "__main__":
    def build(adj: List[List[int]]) -> Optional[Node]:
        nodes = [Node(i + 1) for i in range(len(adj))]
        for i, nbs in enumerate(adj):
            nodes[i].neighbors = [nodes[j - 1] for j in nbs]
        return nodes[0] if nodes else None

    def to_adj(node: Optional[Node]) -> List[List[int]]:
        if node is None:
            return []
        seen = {}

        def walk(cur: Node) -> None:
            if cur.val in seen:
                return
            seen[cur.val] = [nb.val for nb in cur.neighbors]
            for nb in cur.neighbors:
                walk(nb)

        walk(node)
        return [seen[i] for i in range(1, len(seen) + 1)]

    adj = [[2, 4], [1, 3], [2, 4], [1, 3]]
    orig = build(adj)
    cloned = cloneGraph(orig)
    assert to_adj(cloned) == adj
    assert cloned is not orig
    assert cloned.neighbors[0] is not orig.neighbors[0]
    assert cloneGraph(None) is None
    print("ok")
```

## 复杂度

时间 $O(V+E)$，空间 $O(V)$（哈希 + 递归栈或队列）。每个节点与每条边处理一次。

## 边界

- 空节点：直接返回 `None`。
- 单节点无邻居：新建一个同值节点，`neighbors` 为空。
- 两点互为邻居（最小环）：必须先把新节点放进哈希再走邻居，否则 `a.neighbors → b → a` 死递归。

## 追问

- **浅拷贝错在哪？** `copy.neighbors = cur.neighbors` 只复制了列表引用，邻居仍是旧图对象。改新图某个邻居的 `val` 或邻接，旧图一起变；有环时甚至分不清「新图」边界。深拷贝要求每个旧节点对应唯一新节点，边只接在新节点之间。链表带随机指针是同一套路，见 LC 138，独立卡 `lc-138-copy-list-with-random-pointer`。

```python
from collections import deque

def cloneGraphBFS(node):
    if node is None:
        return None
    mp = {node: Node(node.val)}
    q = deque([node])
    while q:
        cur = q.popleft()
        for nb in cur.neighbors:
            if nb not in mp:
                mp[nb] = Node(nb.val)
                q.append(nb)
            mp[cur].neighbors.append(mp[nb])
    return mp[node]
```

- **有向图 / 带权图？** 哈希「旧 $\to$ 新」不变。有向图只按出边复制，不要补反向。带权则邻居改成 `(邻节点, 权)`，复制时权原样抄，邻节点走哈希。仍是先登记再递归，才能处理环。

```python
class WNode:
    def __init__(self, val=0):
        self.val = val
        self.edges = []  # (neighbor, weight)


def cloneWeighted(node):
    mp = {}

    def dfs(cur):
        if cur in mp:
            return mp[cur]
        copy = WNode(cur.val)
        mp[cur] = copy
        copy.edges = [(dfs(nb), w) for nb, w in cur.edges]
        return copy

    return dfs(node) if node else None
```
