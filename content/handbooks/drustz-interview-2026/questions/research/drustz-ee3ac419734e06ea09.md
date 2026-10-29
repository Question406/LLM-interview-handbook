---
id: drustz-ee3ac419734e06ea09
section: research
order: 119
level: A
title: Infection Spread / Cellular Automata（传染病网格模拟）——OpenAI 第一高频 coding 题，33 帖
quick: >-
  supplemental-research-note · Infection Spread / Cellular
  Automata（传染病网格模拟）——OpenAI 第一高频 coding 题，33 帖
companies:
  - openai
tags:
  - DrustZ
  - supplemental-research-note
  - 公司面试 · 补充研究笔记
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json
    type: primary
  - title: 作者记录的原始来源
    url: 'https://www.1point3acres.com/interview/problems/company/openai'
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

官方题库免费预览原文：'M×N grid with infected cells (X) and susceptible cells (./*); infection propagates each day under escalating rules. 5 sub-parts in 60 min; passing bar is typically solving the first 3 with clean BFS.' 角色 SWE/MLE/RE/RS，phone screen+tech screen，60min，status='ai-forbidden'（明确禁 AI 工具），首报 2025-11-01，last_asked 2026-06-29。变体细节（断档期帖子）：thread-1176381（2026-05-11, MLE 店面《开放爱-传染病(1-4问)》）四问=感染扩散/免疫 immunity/康复 recovery/细胞死亡 cell death；thread-1175440（2026-05-03, MLE 挂经）=virus spread simulation + immunity modeling，求迭代感染天数与 herd immunity 时间线；thread-1177818（2026-05-24 onsite）算法轮=植物感染 5 小问（回复区在问第 4 问 death 的条件）；thread-1173136（2026-04-15, B2B 岗挂经）coding 轮即 2D matrix infection，楼主只做到 part3 挂掉，『面完才发现有原题，亏死…把地里题都刷一遍吧』，3 天出 feedback；thread-1174012（2026-04-22）经典 infection+变体+debug；thread-1178391（2026-05-29）geography+plant infection。OJ 变体：'Minimum Time to Infect a Network'、'Plant Infection by Neighbor Count'、'Infection Spread with Immune Units and Expiring Contagiousness'、'Minimum Time to Infect All Plants'、'Cell Simulation / Conway's Game of Life'。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
