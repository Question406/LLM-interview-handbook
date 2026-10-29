---
id: drustz-e817ba938304eea1e8
section: research
order: 137
level: A
title: >-
  OpenAI · 其余 5 道 Coding（Monster Team Battle / Shard Rebalancing / Design IP
  Range Iterator / Design a Spreadsheet / Data Labeling Task Scheduler）
quick: >-
  supplemental-research-note · OpenAI · 其余 5 道 Coding（Monster Team Battle /
  Shard Rebalancing / Design IP Range Iterator / Design a Spreadsheet / Data
  Labeling Task Scheduler）
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
    url: 'https://www.hack2hire.com/question-bank/companies/openai/coding-questions'
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

OpenAI Coding 题库剩余5题（各有独立 practice 页，postId 见下）：(1) Monster Team Battle [Medium, Simulation, id 69a3a99d6e73e4abccc9c106]：模拟两支有序怪物队伍确定性回合制战斗，按'主攻→死亡检查→有条件反击→二次死亡检查→指针推进'严格顺序处理，输出完整战斗日志；提示：为每队维护独立索引而非改原列表。(2) Shard Rebalancing [Medium, id 69a3c4396e73e4abccc9c14c]：分布式 KV 分片，shards 格式 '&lt;id&gt;:&lt;start&gt;:&lt;end&gt;' 各负责闭区间；实现 rebalance(limit, shards) 使任一 key 被覆盖的分片数不超 limit，并填补 gap；提示：按 start 排序 + min-heap 存 accepted 分片终点，扫描线贪心。(3) Design IP Range Iterator [Medium, id 69a5f7bb3d95612a1782be6a]：前向 IPv4 迭代器，hasNext/next 均 O(1)；提示：把 IPv4 当 base-256 大整数，位移/模256 取回各 octet。(4) Design a Spreadsheet with Formula Evaluation [Medium, LeetCode 3484 变体, id 69f789f030f41dfd539fc6bb]：A-Z 列 1-100 行，cell 可存数值或引用其他 cell 的公式，getCell 时动态求值；提示：DFS 解引用 + getCell 内每次新建 memo cache；follow-up：如何检测/防止循环依赖。(5) Data Labeling Task Scheduler [Hard, Greedy, id 69fc0e7f574d87bc49005a3c]：给 totalTask/totalModel/totalHuman/k，分配 [task,model,human]，使每个 human 完成至少 k 个不重复 task，返回任一合法方案或空；提示：先算单 human 最大可处理 unique task 数判可行性，分轮次每轮每人一个分配，用 task 索引模运算保证 (task,human) 不重复。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/openai/coding-questions)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
