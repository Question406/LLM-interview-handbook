---
id: p3a-xai-pipeline-critical-path
section: xai
order: 750
level: S
title: xAI：数据流水线：无限并行下的目标完成时间
quick: >-
  机器无限时，任务等最晚就绪的输入到达后开始，再加自身耗时得到完成时间。只在目标依赖子图上拓扑传播并检测环，时间和空间都是 O(V +
  E)，长链用显式栈与队列处理。
companies:
  - xai
tags:
  - xAI
  - Coding
  - Frontier-2026-10
  - 完整编程练习
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres xAI source
    url: >-
      https://www.1point3acres.com/interview/problems/98b3005e-64bf-49ac-9c1f-abfdc73e7189
    type: secondary
---

## 题目描述

给定任务依赖与执行时长，计算目标数据最早可用的时间。机器数量不限，不存在排队或资源竞争；一个任务只有在它的全部输入数据都已就绪时才能开始。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `critical_path(tasks, goal) -> int`：`tasks` 是 `(inputs, output, duration)` 的列表，返回 `goal` 最早可用的时间。
- 每个 `output` 最多一个生产者，`duration >= 0`。
- 没有生产者的数据是源数据，在时刻 0 就绪；没有输入的任务从时刻 0 开始。机器数量不限。
- 只有目标的依赖子图里有环时才抛 `ValueError`，无关的环不影响结果。
- 节点和边都不超过 $2 \times 10^5$，实现不能依赖递归。

### 示例

```text
tasks = [(["a", "b"], "c", 30), (["b"], "d", 15), (["c", "d"], "g", 60)]
critical_path(tasks, "g") -> 90
critical_path(tasks, "a") -> 0
```

## 解题思路与参考答案

我会在目标的依赖子图上按拓扑序计算关键路径。机器无限时，互不依赖的任务能同时执行，不需要为机器排队。于是一个任务的开始时间是它所有输入就绪时间的最大值，而不是它们的和；它的完成时间等于开始时间加上自身耗时。目标的答案就是依赖图上从源数据到目标的最长路径，也就是关键路径。

## 题目

数据流水线由若干任务组成，每个任务读入一组数据、产出一个数据，并耗时固定的时间。任务要等全部输入就绪才能开始，机器数量不限。给定一个目标数据，求它最早什么时候可以产出。

> 来源：一亩三分地 xAI 题目页（2026-10-18 读取），读到了题干：任务要等全部输入、每个输出最多一个生产者、没有生产者的输入在时刻 0 可用。原帖没写的条件不算已确认的面试事实；下面的接口、约束和测试是手册补的练习约定。

实现分三步：

1. 建表：每个输出对应它的生产者（输入集合和耗时），顺便检查一个输出不能有两个生产者、耗时不能为负。
2. 从目标出发反向找出它依赖的全部数据，只在这个子图上计算。这样与目标无关的环或坏数据不会干扰结果。
3. 在子图上按拓扑序（Kahn 算法）传播就绪时间。

节点数可能到 $2 \times 10^5$，长链会超过 Python 的递归深度限制，所以全程用显式栈和队列，不用递归。

需要和面试官确认的点：同一个输出能否有多个生产者（这里不允许），目标依赖里有环怎么办（这里抛 `ValueError`），零输入的任务从什么时候开始（时刻 0）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `critical_path(tasks, goal) -> int`：`tasks` 是 `(inputs, output, duration)` 的列表，返回 `goal` 最早可用的时间。
- 每个 `output` 最多一个生产者，`duration >= 0`，否则抛 `ValueError`。
- 没有生产者的数据是源数据，在时刻 0 就绪；没有输入的任务从时刻 0 开始。机器数量不限。
- 只有目标的依赖子图里有环时才抛 `ValueError`，无关的环不影响结果。
- 节点和边都不超过 $2 \times 10^5$，实现不能依赖递归。

### 输入输出示例

```text
tasks = [(["a", "b"], "c", 30), (["b"], "d", 15), (["c", "d"], "g", 60)]
critical_path(tasks, "g") -> 90
critical_path(tasks, "a") -> 0
```

g 要等 c（30 时就绪）和 d（15 时就绪），所以 30 时开始，90 时完成。a 是源数据，时刻 0 就可用。

### 解题思路与正确性

`ready_time[node]` 在节点出队前暂存「它的输入里最晚的就绪时间」，也就是任务的开始时间。拓扑序保证节点出队时，它的所有输入都已经出队并算好了最终就绪时间，所以这个最大值是准确的；出队时再加上自身耗时，就得到它的就绪时间。源数据没有生产者，就绪时间保持 0。

如果依赖子图里有环，环上的节点入度永远降不到 0，处理的节点数会少于子图大小，据此判定有环。

这个模型假设机器无限、每个输出只有一个生产者，也没有资源互斥。

### 完整参考实现（Python 3）

```python
from collections import deque


def _build_producers(tasks):
    """output -> (输入集合, 耗时)。每个数据最多一个生产者，耗时非负。"""
    producers = {}
    for inputs, output, duration in tasks:
        if output in producers:
            raise ValueError(f"{output!r} has more than one producer")
        if duration < 0:
            raise ValueError(f"negative duration for {output!r}: {duration}")
        producers[output] = (set(inputs), duration)
    return producers


def _ancestors(producers, goal):
    """goal 以及它直接或间接依赖的所有数据（迭代 DFS，避免递归深度上限）。"""
    needed = set()
    stack = [goal]
    while stack:
        node = stack.pop()
        if node in needed:
            continue
        needed.add(node)
        if node in producers:
            stack.extend(producers[node][0])
    return needed


def critical_path(tasks, goal):
    """机器无限、任务等全部输入就绪才开始时，goal 最早什么时候可用。"""
    producers = _build_producers(tasks)
    needed = _ancestors(producers, goal)  # 只看 goal 的依赖子图，无关的环不影响结果

    pending = {node: 0 for node in needed}  # 还没就绪的输入个数
    consumers = {node: [] for node in needed}
    ready_time = {node: 0 for node in needed}  # 源数据在时刻 0 就绪
    for node in needed:
        if node in producers:
            inputs, _ = producers[node]
            pending[node] = len(inputs)
            for parent in inputs:
                consumers[parent].append(node)

    # Kahn 拓扑序：出队时所有输入都已处理，ready_time 暂存的是「最晚的输入就绪时间」
    queue = deque(node for node in needed if pending[node] == 0)
    processed = 0
    while queue:
        node = queue.popleft()
        processed += 1
        if node in producers:
            ready_time[node] += producers[node][1]  # 开始时间 + 自身耗时
        for child in consumers[node]:
            ready_time[child] = max(ready_time[child], ready_time[node])
            pending[child] -= 1
            if pending[child] == 0:
                queue.append(child)

    if processed != len(needed):
        raise ValueError(f"dependency cycle on the way to {goal!r}")
    return ready_time[goal]
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert critical_path(tasks, "g") == 90` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")


tasks = [(["a", "b"], "c", 30), (["b"], "d", 15), (["c", "d"], "g", 60)]

# 两条前置链取较长的一条：max(30, 15) + 60
assert critical_path(tasks, "g") == 90

# 源数据在 0 时刻就绪
assert critical_path(tasks, "a") == 0

# 与目标无关的环不影响结果
assert critical_path(tasks + [(["z"], "z", 1)], "g") == 90

# 目标依赖子图里有环
expect_value_error(critical_path, [(["b"], "a", 1), (["a"], "b", 1)], "a")

# 没有输入的任务从 0 开始
assert critical_path([([], "a", 7)], "a") == 7

# 同一个输出有两个生产者、负耗时
expect_value_error(critical_path, [([], "a", 1), ([], "a", 2)], "a")
expect_value_error(critical_path, [([], "a", -1)], "a")

# 长链：不能依赖递归
chain = [([f"n{i}"], f"n{i + 1}", 1) for i in range(5000)]
assert critical_path(chain, "n5000") == 5000
```

### 复杂度与追问

设目标依赖子图有 V 个节点、E 条依赖边。找祖先、建图和拓扑传播都是 O(V + E) 时间和空间。

- 如果同一个数据可以由多个任务产出，就绪时间变成各个生产者完成时间的最小值，图上同时有「全部输入取最大」和「多个来源取最小」两种节点，需要重新定义问题。
- 如果 worker 数量有限，问题变成带依赖的多机调度，一般是 NP 难的。关键路径长度只是完成时间的下界，不能直接当答案，可以用列表调度这类启发式方法求近似解。
