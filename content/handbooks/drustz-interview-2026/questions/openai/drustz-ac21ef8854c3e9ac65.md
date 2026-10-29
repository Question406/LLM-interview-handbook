---
id: drustz-ac21ef8854c3e9ac65
section: openai
order: 122
level: A
title: Infectious Disease Spread (Infection Propagation)
quick: >-
  original-structured-preparation-guide · Infectious Disease Spread (Infection
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
      https://www.1point3acres.com/interview/problems/e64046b0-c762-467b-905f-4e4293875d94
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Infectious Disease Spread：传播时间的图模型

> **证据边界**：标题只确认 infection propagation。相关面经一类是类似 Rotting Oranges 的 **4 邻域** BFS，另一份本地原始面经明确为 **8 邻域**植物传播，因此当前 UUID 的邻接定义尚不能确认。下面给单位时间传播的通用图解法，`directions` 由题面决定。

## 题意模型

把每个可感染格看成图节点，相邻关系看成边。所有初始感染节点在时间 `0` 同时开始传播，每经过一条边耗时一天；免疫或障碍格（若有）不建边。求每格的最早感染时间、达到稳定的时间，或判断能否感染全部目标格。

例如一行 `X..` 的最早时间为 `[0,1,2]`；若二维网格只允许四方向，对角格需走两步，而允许八方向时只需一步。

## 多源 BFS

将全部感染源一次入队，距离设为 `0`。弹出 `(cell, time)` 后，只访问尚未感染的合法邻居，赋值 `time+1`。队列天然按时间递增，故第一次访问就是最早感染时间；最后一次成功感染的时间就是稳定时间。

```text
queue = deque(all_sources)
while queue:
    u = pop_left()
    for v in neighbors(u, directions):
        if v is susceptible and unseen:
            dist[v] = dist[u] + 1; push(v)
```



如果健康格需至少 `K>1` 个感染邻居，则首次到达不再足够，要改为按层累计邻居计数；有不同传播耗时则改多源 Dijkstra。

## 复杂度与边界

网格版时间和空间均 `O(RC)`，一般图为 `O(V+E)`。无感染源且仍有健康格通常无法完成；初态无健康格返回 `0`。还应确认不可达格返回 `-1` 还是只求稳定时间，并测试多个感染源相遇、障碍封闭、边界格及 4/8 邻域差异。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/e64046b0-c762-467b-905f-4e4293875d94)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
