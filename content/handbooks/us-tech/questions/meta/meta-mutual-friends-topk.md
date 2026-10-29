---
id: meta-mutual-friends-topk
section: meta
order: 923
level: A
title: "Meta AI Coding：按 mutual friends 生成 top-K recommendations"
quick: "我会从 user 的每个 friend 走一跳。每遇到一个合格候选就加一分：因为 neighbor set 没有重复，同一个 friend 恰好贡献一次 mutual-friend count。"
companies:
  - meta
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开报告题型改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：Meta AI Coding：按 mutual friends 生成 top-K recommendations"
    url: "https://aceoffer.app/interviews/ai-coding"
    type: secondary
---

## 题目描述

来源：AceOffer 的公开 AI coding 综述列出 Meta friend recommendation 项目。下面将 ranking 与 graph 输入固定成可测试的 Python 模块。

### 输入、接口与规则

实现 `recommend(graph, user, k) -> list[tuple[int,int]]`。graph 是无向简单图，以 dict 映射整数 user ID 到 neighbor set，包含所有 nodes，边双向一致，无 self-loops。user 存在；k 为非负整数。候选必须与 user 不同、不是现有 friend，并且至少有一个 mutual friend。

候选 score 是共同 friends 的数量。返回最多 k 个 `(candidate_id, score)`，按 score 降序、同分 ID 升序；k=0 返回空列表，不修改 graph。不要对所有用户两两求集合交集；应从 user 的 friends 出发遍历 two-hop neighborhood，并说明 hub 节点对运行时间的影响。

### 输入输出示例

```text
graph={0:{1,2},1:{0,3,4},2:{0,3},3:{1,2},4:{1}}
recommend(graph,0,2) -> [(3,2),(4,1)]。
recommend(graph,3,1) -> [(0,2)]。
```

## 回答思路

> **Situation / Task：** 只推荐非好友，score 是共同 neighbors 数量。  
> **Approach / Why：** 遍历 friends 的 neighbors 计数，再用 bounded heap 取 top-K。  
> **Result / Check：** 检查排除自己与现有 friend、并列排序和 hub 扩展成本。

## 解题思路与参考答案

我会从 user 的每个 friend 走一跳。每遇到一个合格候选就加一分：因为 neighbor set 没有重复，同一个 friend 恰好贡献一次 mutual-friend count。

这样只访问 two-hop neighborhood，不需要扫描全站所有用户。取 top-K 时使用 score 降序、ID 升序的统一 key。大 hub 仍然可能很贵，线上是否限制 hub 的贡献属于 ranking 规则变化，需要另外评估。

### 完整参考实现

```python
from collections import Counter
from heapq import nsmallest


def recommend(graph, user, k):
    if k < 0:
        raise ValueError('k must be nonnegative')
    if k == 0:
        return []
    blocked = graph[user] | {user}
    counts = Counter()
    for friend in graph[user]:
        for candidate in graph[friend]:
            if candidate not in blocked:
                counts[candidate] += 1
    best = nsmallest(k, counts, key=lambda node: (-counts[node], node))
    return [(node, counts[node]) for node in best]
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
g = {0: {1, 2}, 1: {0, 3, 4}, 2: {0, 3}, 3: {1, 2}, 4: {1}}
assert recommend(g, 0, 2) == [(3, 2), (4, 1)]
assert recommend(g, 3, 1) == [(0, 2)]
assert recommend(g, 0, 0) == []
from random import Random

rng = Random(3)
for _ in range(80):
    g = {i: set() for i in range(20)}
    for i in g:
        for j in range(i):
            if rng.random() < 0.2:
                g[i].add(j)
                g[j].add(i)
    expected = [
        (j, len(g[0] & g[j])) for j in g if j != 0 and j not in g[0] and g[0] & g[j]
    ]
    expected.sort(key=lambda item: (-item[1], item[0]))
    assert recommend(g, 0, 5) == expected[:5]
print('recommendation tests passed')
```

## 复杂度与追问

令 W 为 user 的 friends 的 degree 之和、C 为候选数量。时间 `O(W+C*log(max(2,K)))`，空间 `O(C+K)`；K≥C 时实现可能排序，仍不超过这个上界。追问预计算与增量更新时，先说明 graph freshness 要求。
