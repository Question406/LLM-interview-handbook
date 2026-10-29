---
id: drustz-9e2c7c51a81f989e1a
section: openai
order: 68
level: A
title: Infection Spread on a Network (Graph Propagation)
quick: >-
  original-structured-preparation-guide · Infection Spread on a Network (Graph
  Propagation)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/66dfe55d-a29b-41a6-b782-b049ef97d8ab
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Infection Spread on a Network

> 标题是一般 graph，旧正文固定为二维网格。传播阈值和边方向未公开，因此下面给出可配置图算法。

## 标准规则：一个感染邻居即可传播

用 adjacency list；所有初始感染节点以时间 0 同时入队。多源 BFS 第一次到达节点的层数就是最早感染时间。

```text
dist[seed] = 0 for all seeds
for u popped from queue:
  for v in adjacency[u]:
    if v unvisited:
      dist[v] = dist[u] + 1
      enqueue(v)
```



若规则是至少 `r` 个感染邻居，维护 `infected_neighbor_count`，按层批量处理；本层达到阈值的节点只能在下一层感染，保持同步。带权传播改为多源 Dijkstra。

## 复杂度与边界

BFS/阈值版 `O(V+E)`，加权版 `O((V+E) log V)`。覆盖有向/无向、空 seeds、断连、重复边、自环、阈值大于度数和同一分钟同步传播。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/66dfe55d-a29b-41a6-b782-b049ef97d8ab)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
