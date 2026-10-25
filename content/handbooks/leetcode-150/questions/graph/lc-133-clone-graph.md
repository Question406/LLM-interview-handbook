---
id: lc-133-clone-graph
section: graph
order: 3
level: A
title: LC 133 · 克隆图
quick: "用哈希表记「旧节点 $\\to$ 新节点」，DFS 或 BFS 克隆邻居，遇到已经建过的节点直接复用。新节点要先登记再递归邻居，这样才能处理环。"
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

## 题目描述

给定一张无向连通图中的起始节点，返回整张图的深拷贝。每个节点有整数属性 val 和邻居列表 neighbors；新图必须保留节点值和邻接关系，但所有节点都应是新对象，任何新图中的边都不能指向原图节点。

### 输入与输出

实现 `cloneGraph(node: Optional[Node]) -> Optional[Node]`。返回与输入起始节点对应的新节点；空图返回 `None`。示例使用邻接表：第 i 个内层列表列出值为 i+1 的节点的邻居值，非空图从值为 1 的节点开始。实际调用传入节点对象，不是邻接表。

### 约束

- 节点数为 0 到 100，节点值为 1 到 100 且互不相同。
- 图没有重边和自环；非空时从给定节点可到达全部节点。

### 示例

```text
输入：adjList = [[2,4],[1,3],[2,4],[1,3]]
输出：[[2,4],[1,3],[2,4],[1,3]]
```

输出邻接表与输入相同仅说明结构一致，实际返回的节点及其所有邻居对象还必须与原图分离。

## 解题思路与参考答案

## 题意

给一张无向连通图，每个节点有整数值 `val` 和邻居列表 `neighbors`。返回图的深拷贝：新节点值相同、邻接关系相同，但对象全是新的。空图返回空。

## 思路

我会用 DFS 加一张「旧节点 $\to$ 已克隆的新节点」的哈希表。图里有环，像树那样直接递归会在环上无限循环，哈希表保证每个旧节点只建一次新节点。

DFS 时，当前旧节点已经在表里，就直接返回对应的新节点；否则先 `new Node(val)` 登记进表，再递归克隆邻居、填进 `neighbors`。顺序一定是先登记再递归。拿最小的环 `1 — 2` 来说，克隆 `1` 时先把它的副本放进表，递归到 `2`，`2` 的邻居又是 `1`，这时查表直接拿到 `1` 的副本，递归就停住了。

BFS 也一样：队列扩展邻接，哈希表保证每个旧节点只建一次。开口一句话：先放进哈希表，再走邻居。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
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
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(V+E)$，每个节点和每条边各处理一次；空间 $O(V)$，是哈希表加上递归栈或队列。

## 边界

空节点直接返回 `None`。单节点没有邻居时，新建一个同值节点，`neighbors` 为空。两点互为邻居（最小环）时，必须先把新节点放进哈希表再走邻居，否则 `a.neighbors → b → a` 会无限递归。

## 追问

**浅拷贝错在哪？**
`copy.neighbors = cur.neighbors` 只复制了列表引用，邻居还是旧图里的对象。改新图某个邻居的 `val` 或邻接，旧图跟着变；有环时甚至分不清「新图」的边界在哪。深拷贝要求每个旧节点对应唯一一个新节点，边只连在新节点之间。下面附的是 BFS 版写法。链表带随机指针是同一套路，见 LC 138，独立卡 `lc-138-copy-list-with-random-pointer`。

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

**有向图或带权图呢？**
「旧 $\to$ 新」的哈希表不变。有向图只按出边复制，不要补反向边。带权图把邻居换成 `(邻节点, 权)`，复制时权原样抄，邻节点走哈希表。仍然要先登记再递归，才能处理环。

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
