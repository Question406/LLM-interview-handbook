---
id: openai-modular-addition-bfs
section: openai
order: 930
level: A
title: "OpenAI OA：通过 modular additions 到达 target 的最少操作数"
quick: "我会先把每个 addition 对 modulus 取模并去重。实际状态最多只有 modulus 个，绕了一圈回到同一个 residue 后就不必继续重复扩展。"
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
  - title: "公开来源：OpenAI OA：通过 modular additions 到达 target 的最少操作数"
    url: "https://aceoffer.app/interviews/oai_minimum_steps_to_target_number_via_modular_addition"
    type: secondary
---

## 题目描述

来源：AceOffer 公开 OA 目录列出 minimum steps via modular addition，并标注 BFS。下面采用可选 step 集合，modulus 与返回规则由手册设定。

### 输入、接口与规则

实现 `modular_steps(modulus, start, target, additions) -> int`。modulus 是 1..100000 的整数，start 与 target 在 0..modulus-1。additions 是最多 30 个整数，允许负数、零与重复。每次可任意选一个 a，令当前状态 x 变为 `(x+a) % modulus`，每次 cost=1，同一个 a 可无限次使用。

返回从 start 到 target 的最少操作数；不可达时返回 -1。start=target 返回 0，空 additions 且起终点不同则返回 -1。不修改输入。请把状态空间限定在 residues 上，避免在未取模的整数轴上搜索，并说明单一 addition 时可以怎样用 gcd 改写可达性判断。

### 输入输出示例

```text
modulus=7, start=0, target=3, additions=[2,3] -> 1。
modulus=6, start=0, target=3, additions=[2] -> -1。
modulus=7, start=1, target=0, additions=[-1] -> 1。
```

## 回答思路

> **Situation / Task：** 状态是 residue，一次 addition 是一条有向 edge。  
> **Approach / Why：** BFS 搜索至多 modulus 个状态，先对 steps 取模去重。  
> **Result / Check：** 小 modulus 与独立 shortest-path DP 比较，检查负数和不可达。

## 解题思路与参考答案

我会先把每个 addition 对 modulus 取模并去重。实际状态最多只有 modulus 个，绕了一圈回到同一个 residue 后就不必继续重复扩展。

所有操作 cost 都是一，所以 BFS 得到最少操作数。单一 addition 可以用 gcd 判断能否到达；多个 additions 时，可达性判断并不能直接给出最少步数，仍然需要求 shortest path。

### 完整参考实现

```python
from collections import deque


def modular_steps(modulus, start, target, additions):
    steps = {a % modulus for a in additions}
    queue = deque([start])
    distance = [-1] * modulus
    distance[start] = 0
    while queue:
        value = queue.popleft()
        if value == target:
            return distance[value]
        for step in steps:
            nxt = (value + step) % modulus
            if distance[nxt] == -1:
                distance[nxt] = distance[value] + 1
                queue.append(nxt)
    return -1
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert modular_steps(7, 0, 3, [2, 3]) == 1
assert modular_steps(6, 0, 3, [2]) == -1
assert modular_steps(7, 1, 0, [-1]) == 1
assert modular_steps(1, 0, 0, []) == 0
from math import inf

for m in range(2, 12):
    for additions in [[], [0], [2], [-1, 3], [2, 4, 2]]:
        dist = [inf] * m
        dist[0] = 0
        for _ in range(m):
            new = dist[:]
            for u in range(m):
                for a in additions:
                    new[(u + a) % m] = min(new[(u + a) % m], dist[u] + 1)
            dist = new
        for target in range(m):
            assert modular_steps(m, 0, target, additions) == (
                -1 if dist[target] == inf else dist[target]
            )
print('modular additions tests passed')
```

## 复杂度与追问

设 M 为 modulus、A 为 distinct additions 数，时间 `O(M*A+len(additions))`，空间 `O(M+A)`。追问每种操作 cost 不同时改为 Dijkstra；不要继续使用 FIFO queue 假设最短。
