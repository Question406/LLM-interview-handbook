---
id: drustz-5a4ea6dfa1aaf1344a
section: openai
order: 57
level: A
title: Minimum Time to Infect All Plants
quick: original-structured-preparation-guide · Minimum Time to Infect All Plants
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
      https://www.1point3acres.com/interview/problems/52d376f2-a7b9-55d5-90eb-a06a88acae5b
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Minimum Time to Infect All Plants：感染全部植物的最短时间

> **证据边界**：标题确认输出是“全部植物感染的最短时间”。本地资料同时存在 4 邻域（类似 Rotting Oranges）与 8 邻域面经，当前 UUID 的完整约束未公开；下面描述单位时间、一个感染邻居即可传播的基础版，并把方向集合设为参数，不冒充精确原题。

## 题目与例子

网格中 `X` 是已感染植物、`.` 是健康植物，障碍或免疫格（若题面有）不可经过。每一天，所有当前 `X` 同时感染相邻的健康格。求最早多少天能让所有可要求感染的植物都变成 `X`；存在永远到不了的健康格时返回 `-1`。

例如一行 `X...` 且只允许上下左右相邻，感染时间依次为 `0,1,2,3`，答案是 `3`。若中间有永久障碍，则右侧健康格不可达，答案为 `-1`。

## 多源 BFS

把所有初始 `X` 以距离 `0` 一起入队。每次首次访问健康邻居，就记录 `dist+1` 并入队；因为所有边耗时都是一天，BFS 的首次到达时间就是最短感染时间。答案是最后一个健康格的距离，而不是队列弹出次数。

```text
queue = 所有初始感染点
while queue:
    从当前格扩展 directions 中尚未感染的健康邻居
return max_distance if healthy_left == 0 else -1
```



## 复杂度与边界

时间 `O(RC)`，空间 `O(RC)`。没有健康植物返回 `0`；有健康植物但无感染源返回 `-1`。应确认免疫格是否从“必须感染总数”中排除、邻居是 4 个还是 8 个、感染是否需要阈值；若阈值大于 1，就不能直接用首次到达 BFS，而要维护每日感染邻居计数。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/52d376f2-a7b9-55d5-90eb-a06a88acae5b)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
