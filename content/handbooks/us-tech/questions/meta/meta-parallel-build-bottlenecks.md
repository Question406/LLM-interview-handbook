---
id: meta-parallel-build-bottlenecks
section: meta
order: 927
level: A
title: "Meta：找出 parallel build 中独占一个 time step 的 targets"
quick: "我会先确认 bottleneck 的定义。按这题规则，只要某个 step 只有一个 target，它就要返回；这与一般 scheduling 中的 critical path 不是同一个问题。"
companies:
  - meta
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：Meta：找出 parallel build 中独占一个 time step 的 targets"
    url: "https://landthelab.com/questions/find-bottleneck-dependencies-in-a-parallel-build"
    type: secondary
---

## 题目描述

来源：Land the Lab 标注 Meta / Databricks 的公开练习。此处 bottleneck 沿用该页的具体定义：某一 time step 只有一个 target 在执行；重复 edges 的处理由手册明确。

### 输入、接口与规则

实现 `find_bottlenecks(n, edges) -> list[int]`。输入 targets 为 0..n-1，n 可为 0；每个 target 执行恰好一个 time step，可用 builders 数量无限。edge (u,v) 表示 v 必须在 u 完成后的下一个 step 或更晚执行。每个 target 都在依赖满足后尽早开始；没有 prerequisites 的 targets 在 step 1 执行。

若某个 step 恰好只有一个 target 执行，该 target 称为本题的 bottleneck；按执行 step 顺序返回它们。重复 edges 忽略；输入出现 cycle 抛 ValueError。n≤100000，edges≤200000，端点合法且不含 self-loop。不修改输入；这里的定义与“是否处于 critical path”需要分开解释。

### 输入输出示例

```text
n=4, edges=[(0,1),(0,2),(1,3),(2,3)] -> [0,3]。
三个 steps 分别为 {0}、{1,2}、{3}。
n=5, edges=[(0,1),(2,3),(3,4)] -> [4]。
```

## 回答思路

> **Situation / Task：** 每个 target cost=1、无限 builders；找只有一个正在执行的 step。  
> **Approach / Why：** Kahn topological traversal 分 batch，每批是一个执行 step。  
> **Result / Check：** 检查 diamond、chain、重复 edge、cycle 与空图。

## 解题思路与参考答案

我会先确认 bottleneck 的定义。按这题规则，只要某个 step 只有一个 target，它就要返回；这与一般 scheduling 中的 critical path 不是同一个问题。

每次取出当前全部 indegree=0 的 nodes 作为一个 batch，执行完后才把新 ready 的 nodes 放入下一批。batch 长度为一就记录这个 target；最后检查处理数量，顺便检测 cycle。

### 完整参考实现

```python
def find_bottlenecks(n, edges):
    graph = [[] for _ in range(n)]
    indegree = [0] * n
    for u, v in set(edges):
        graph[u].append(v)
        indegree[v] += 1
    ready = [i for i in range(n) if indegree[i] == 0]
    count = 0
    result = []
    while ready:
        if len(ready) == 1:
            result.append(ready[0])
        next_ready = []
        for u in ready:
            count += 1
            for v in graph[u]:
                indegree[v] -= 1
                if indegree[v] == 0:
                    next_ready.append(v)
        ready = next_ready
    if count != n:
        raise ValueError('cycle')
    return result
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert find_bottlenecks(4, [(0, 1), (0, 2), (1, 3), (2, 3)]) == [0, 3]
assert find_bottlenecks(5, [(0, 1), (2, 3), (3, 4)]) == [4]
assert find_bottlenecks(0, []) == []
assert find_bottlenecks(1, []) == [0]
assert find_bottlenecks(3, [(0, 1), (0, 1), (1, 2)]) == [0, 1, 2]
try:
    find_bottlenecks(2, [(0, 1), (1, 0)])
except ValueError:
    pass
else:
    raise AssertionError('cycle accepted')
print('build graph tests passed')
```

## 复杂度与追问

去重 edges 后时间、空间均为 `O(N+E)`。追问不同 durations 时不能继续按 BFS batch 当实际 time step，需要改为 earliest finish times，再按照新定义判断并行重叠。
