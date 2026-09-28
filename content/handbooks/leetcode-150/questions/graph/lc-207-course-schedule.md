---
id: lc-207-course-schedule
section: graph
order: 5
level: S
title: LC 207 · 课程表
quick: >-
  先修关系是有向边。能修完当且仅当图无环。拓扑 Kahn 入度为 $0$
  入队，或 DFS 三色判环。时间 $O(V+E)$。
tags:
  - Graph
  - Topo
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 207. 课程表
    url: https://leetcode.cn/problems/course-schedule/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

共 `numCourses` 门课，编号 $0..n-1$。`prerequisites[i] = [ai, bi]` 表示修 `ai` 必须先修 `bi`。问能否修完所有课（存在合法顺序）。

## 思路

边 $b\to a$。有环就死锁。两种写法都要会：

DFS 三色：`0` 未访、`1` 正在访、`2` 已完成。走到 `1` 说明回到当前栈上的点，有环。走完邻居再标 `2`。

Kahn：统计入度，入度为 $0$ 的入队，弹出后把它指向的入度减一。能弹出 $n$ 个则无环。

白板我先画「先修 $\to$ 后修」，再说判环，别把边方向画反。

## 参考代码

```python
from typing import List


def canFinish(numCourses: int, prerequisites: List[List[int]]) -> bool:
    g = [[] for _ in range(numCourses)]
    for a, b in prerequisites:
        g[b].append(a)
    color = [0] * numCourses

    def dfs(x: int) -> bool:
        color[x] = 1
        for y in g[x]:
            if color[y] == 1:
                return False
            if color[y] == 0 and not dfs(y):
                return False
        color[x] = 2
        return True

    return all(color[i] != 0 or dfs(i) for i in range(numCourses))


if __name__ == "__main__":
    assert canFinish(2, [[1, 0]]) is True
    assert canFinish(2, [[1, 0], [0, 1]]) is False
    assert canFinish(1, []) is True
    print("ok")
```

## 复杂度

时间 $O(V+E)$，空间 $O(V+E)$（邻接表 + 颜色或入度队列）。

## 边界

- 无先修：`prerequisites` 为空，每门课入度 $0$，一定能修完。
- 自环 `[0,0]`：边 $0\to 0$，三色立刻碰到灰色，Kahn 入度永不降到 $0$，返回假。
- 多条不连通链：要从所有未访问点启动 DFS，或 Kahn 把所有入度 $0$ 的点先入队；漏掉某个源点会误判。

## 追问

- **输出一种修课顺序？** 把「能否」改成「弹出序列」。Kahn 每次出队写入 `order`，最后长度等于 $n$ 就是拓扑序，否则有环返回空。DFS 则在节点变黑时插入答案头部（后序反过来）。即 LC 210，独立卡 `lc-210-course-schedule-ii`。

```python
from collections import deque

def findOrder(n, prerequisites):
    g = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in prerequisites:
        g[b].append(a)
        indeg[a] += 1
    q = deque([i for i in range(n) if indeg[i] == 0])
    order = []
    while q:
        x = q.popleft()
        order.append(x)
        for y in g[x]:
            indeg[y] -= 1
            if indeg[y] == 0:
                q.append(y)
    return order if len(order) == n else []
```

- **为何不能只看强连通？** 「能修完」的充要条件是有向无环（DAG）。Tarjan / Kosaraju 求 SCC 也能判环：存在大小 $\gt 1$ 的分量，或大小为 $1$ 但带自环，就不能修完。代价更高，还容易漏自环。无向图的连通块与本题无关，先修是有向的。面试用三色 DFS 或 Kahn 即可，不要上 SCC。
