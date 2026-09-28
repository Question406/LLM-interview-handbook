---
id: lc-210-course-schedule-ii
section: graph
order: 6
level: A
title: LC 210 · 课程表 II
quick: >-
  同 207，还要给出一种修课顺序。Kahn：入度为 $0$
  的弹出即序；弹出不足 $n$ 说明有环，返回空数组。
tags:
  - Graph
  - Topo
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 210. 课程表 II
    url: https://leetcode.cn/problems/course-schedule-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

条件同 LC 207。返回任意一种合法修课顺序；不可能修完则返回空数组。

## 思路

Kahn：邻接表 + 入度。先把入度为 $0$ 的课入队，弹出时写入答案，再给后继入度减一、减到 $0$ 就入队。最后长度等于 $n$ 才是完整拓扑序，否则有环。

DFS 也可以：三色判环，节点变成黑色时插入答案头部（后序反过来）。有环立刻停。多种合法序都对，测例不要写死唯一序列，除非自己实现确定。

## 参考代码

```python
from collections import deque
from typing import List


def findOrder(numCourses: int, prerequisites: List[List[int]]) -> List[int]:
    g = [[] for _ in range(numCourses)]
    indeg = [0] * numCourses
    for a, b in prerequisites:
        g[b].append(a)
        indeg[a] += 1
    q = deque([i for i in range(numCourses) if indeg[i] == 0])
    order = []
    while q:
        x = q.popleft()
        order.append(x)
        for y in g[x]:
            indeg[y] -= 1
            if indeg[y] == 0:
                q.append(y)
    return order if len(order) == numCourses else []


if __name__ == "__main__":
    assert findOrder(2, [[1, 0]]) == [0, 1]
    assert findOrder(4, [[1, 0], [2, 0], [3, 1], [3, 2]]) == [0, 1, 2, 3]
    assert findOrder(1, []) == [0]
    assert findOrder(2, [[1, 0], [0, 1]]) == []
    print("ok")
```

## 复杂度

时间 $O(V+E)$，空间 $O(V+E)$。

## 边界

- $n=1$ 无先修：返回 `[0]`。
- 多门入度同为 $0$：拓扑序不唯一，队列弹出顺序依赖入队次序，测例不要写死唯一序列。
- 有环：弹出个数 $\lt n$，返回 `[]`。只问能否修完见 LC 207，独立卡 `lc-207-course-schedule`。

## 追问

- **字典序最小的拓扑序？** Kahn 里用最小堆代替普通队列：每次弹出当前入度为 $0$ 的编号最小的课。正确性：任何时刻可修集合里选最小编号，得到的就是字典序最小合法序。时间 $O((V+E)\log V)$。

```python
import heapq

def findOrderLexicographic(n, prerequisites):
    g = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in prerequisites:
        g[b].append(a)
        indeg[a] += 1
    heap = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        x = heapq.heappop(heap)
        order.append(x)
        for y in g[x]:
            indeg[y] -= 1
            if indeg[y] == 0:
                heapq.heappush(heap, y)
    return order if len(order) == n else []
```

- **只判断能否修完？** 不必存 `order`。Kahn 只计弹出个数是否等于 $n$；或沿用本题文件里的三色 DFS。即 LC 207，独立卡 `lc-207-course-schedule`。

```python
from collections import deque

def canFinish(n, prerequisites):
    g = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in prerequisites:
        g[b].append(a)
        indeg[a] += 1
    q = deque([i for i in range(n) if indeg[i] == 0])
    seen = 0
    while q:
        x = q.popleft()
        seen += 1
        for y in g[x]:
            indeg[y] -= 1
            if indeg[y] == 0:
                q.append(y)
    return seen == n
```
