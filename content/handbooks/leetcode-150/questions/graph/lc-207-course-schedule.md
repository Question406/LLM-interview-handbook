---
id: lc-207-course-schedule
section: graph
order: 5
level: S
title: LC 207 · 课程表
quick: >-
  把先修关系建成有向边，能修完当且仅当这张图没有环。判环用 Kahn（入度为 $0$ 的入队，能弹出全部课就无环）或者 DFS 三色标记，时间
  $O(V+E)$。
tags:
  - Graph
  - Topo
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 207. 课程表
    url: 'https://leetcode.cn/problems/course-schedule/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

你需要修读 numCourses 门课程，编号从 0 到 numCourses-1。每条先修要求 [a,b] 表示开始课程 a 之前必须先完成 b。判断是否存在一个安排，使所有课程都能完成；课程之间如果互相等待而无法开课，应返回否。

### 输入与输出

实现 `canFinish(numCourses, prerequisites) -> bool`。返回能否完成全部课程，不需要给出具体顺序；没有先修要求的课程可以直接修读。

### 约束与约定

- `1 <= numCourses <= 2000`。
- 先修要求有 0 到 5000 条，每条恰好含两个合法课程编号。
- 先修关系不重复。

### 示例

```text
输入：numCourses = 2, prerequisites = [[1,0]]
输出：true
```

示例只要求先修 0 再修 1，因此两门课都可以完成。

[官方原题与完整题面](https://leetcode.com/problems/course-schedule/description/)。

## 解题思路与参考答案

## 题意

共 `numCourses` 门课，编号 $0..n-1$。`prerequisites[i] = [ai, bi]` 表示修 `ai` 之前必须先修 `bi`。问能否修完所有课，也就是是否存在合法顺序。

## 思路

这题就是判有向图有没有环。先修关系建成边 $b\to a$，意思是学完 $b$ 才能学 $a$。如果存在有向环，环上每门课都在等另一门先修完，谁也开不了头，就修不完。

比如 `[[1,0],[0,1]]`：修 1 要先修 0，修 0 又要先修 1，这是一个两门课的环，答案是假。只有 `[[1,0]]` 的话先修 0 再修 1，没问题。

判环我会讲两种。一种是 DFS 三色，`0` 表示没访问过，`1` 表示正在访问（还在递归栈上），`2` 表示已完成。DFS 走到颜色为 `1` 的点，说明绕回了当前栈上的点，有环；所有邻居走完再把自己标成 `2`。参考代码写的就是这个。

另一种是 Kahn：统计每门课的入度，入度为 $0$ 的先入队，弹出一门就把它指向的课入度减一，减到 $0$ 再入队。最后能弹出 $n$ 门就无环。

白板上我会先画清楚「先修 $\to$ 后修」的方向再讲判环，边方向画反的话后面全会错。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert canFinish(2, [[1, 0]]) is True
assert canFinish(2, [[1, 0], [0, 1]]) is False
assert canFinish(1, []) is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(V+E)$，空间 $O(V+E)$，邻接表加上颜色数组或入度队列。

## Edge Cases

没有先修关系时 `prerequisites` 为空，每门课入度都是 $0$，一定能修完。自环 `[0,0]` 就是边 $0\to 0$，三色 DFS 会立刻碰到灰色（状态 `1`）的自己，Kahn 里这门课的入度永远降不到 $0$，两种写法都返回假。图也可能是几条不连通的链，所以 DFS 要从每个没访问过的点都启动一次，Kahn 要把所有入度为 $0$ 的点先入队，漏掉某个源点就会判错。

## 追问

**要输出一种修课顺序呢？**
把「能不能修完」改成记录弹出序列就行。Kahn 每次出队写进 `order`，最后长度等于 $n$ 就是一个拓扑序，否则有环，返回空。DFS 的写法是节点变黑时插到答案头部，也就是后序反过来。这就是 LC 210，单独一张卡 `lc-210-course-schedule-ii`。

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

**用强连通分量来判可以吗？**
可以，但没必要。「能修完」的充要条件是图有向无环（DAG）。Tarjan / Kosaraju 求出 SCC 后，存在大小 $\gt 1$ 的分量，或者大小为 $1$ 但带自环，就修不完。这样代价更高，还容易漏掉自环。无向图的连通块和这题无关，先修关系是有向的。面试用三色 DFS 或 Kahn 就够了，不用上 SCC。
