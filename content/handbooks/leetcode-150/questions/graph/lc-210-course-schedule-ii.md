---
id: lc-210-course-schedule-ii
section: graph
order: 6
level: A
title: LC 210 · 课程表 II
quick: 和 207 一样建图，只是要给出一种修课顺序。用 Kahn 拓扑排序，入度为 $0$ 的课弹出的顺序就是答案；弹出不足 $n$ 门说明有环，返回空数组。
tags:
  - Graph
  - Topo
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 210. 课程表 II
    url: 'https://leetcode.cn/problems/course-schedule-ii/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

共有 `numCourses` 门课程，编号为 0 到 `numCourses-1`。每个先修关系 `[a,b]` 表示必须先完成课程 b，才能开始课程 a。请安排一个包含全部课程、且满足所有先修关系的修课顺序。

### 输入与输出

实现 `findOrder(numCourses, prerequisites) -> List[int]`。若能够修完，返回任意一个合法顺序，每门课恰好出现一次；存在相互依赖而无法修完时返回 `[]`。无先修关系的课程也必须出现在结果中。

### 约束

- `1 <= numCourses <= 2000`。
- 先修关系数量不超过 `numCourses * (numCourses-1)`。
- a、b 都是有效课程编号，`a != b`，且相同的关系不会重复给出。

### 示例

```text
输入：numCourses = 2, prerequisites = [[1,0]]
输出：[0,1]
```

[LeetCode 原题](https://leetcode.com/problems/course-schedule-ii/description/)

## 解题思路与参考答案

## 题意

条件和 LC 207 一样。返回任意一种合法的修课顺序；修不完就返回空数组。

## 思路

我会用 Kahn 拓扑排序，因为它弹出的顺序本身就是修课顺序，顺带还能判环。建邻接表和入度数组，先把入度为 $0$ 的课入队；每弹出一门就写进答案，再把它后继的入度减一，减到 $0$ 的入队。最后答案长度等于 $n$ 才是完整的拓扑序，不够 $n$ 说明剩下的课卡在环里。

看第二个例子 `[[1,0],[2,0],[3,1],[3,2]]`：一开始只有 0 的入度为 $0$，弹出 0 后 1 和 2 的入度都变成 $0$，依次弹出；3 要等 1 和 2 都弹完入度才归零，最后弹出，得到 `[0,1,2,3]`。

DFS 也能做：三色判环，节点变黑时插到答案头部（后序反过来），发现环就立刻停。合法顺序往往不止一种，任何一种都算对。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert findOrder(2, [[1, 0]]) == [0, 1]
assert findOrder(4, [[1, 0], [2, 0], [3, 1], [3, 2]]) == [0, 1, 2, 3]
assert findOrder(1, []) == [0]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(V+E)$，空间 $O(V+E)$。

## Edge Cases

$n=1$ 且没有先修时返回 `[0]`。好几门课入度同时为 $0$ 时，拓扑序不唯一，弹出顺序取决于入队次序，所以测例别写死唯一序列，除非自己的实现顺序是确定的。有环时弹出个数 $\lt n$，返回 `[]`。只问能不能修完是 LC 207，单独一张卡 `lc-207-course-schedule`。

## 追问

**要字典序最小的拓扑序呢？**
把 Kahn 里的普通队列换成最小堆，每次弹出当前入度为 $0$ 的课里编号最小的那门。任何时刻都从可修的集合里挑最小编号，得到的就是字典序最小的合法序。时间变成 $O((V+E)\log V)$。

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

**只判断能不能修完呢？**
那就不用存 `order`。Kahn 只数弹出个数是不是等于 $n$；或者改用三色 DFS。这就是 LC 207，单独一张卡 `lc-207-course-schedule`。

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
