---
id: drustz-508acdb61e83de4407
section: research
order: 46
level: A
title: Onsite coding 真题：LRU cache 分层加需求（持久化/序列化）
quick: supplemental-research-note · Onsite coding 真题：LRU cache 分层加需求（持久化/序列化）
companies:
  - anthropic
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
    url: >-
      https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

Exponent Safeguards SWE 面经：Technical Interview 2 为 LRU cache 实现，随后 layered complexity additions——加文件处理（file handling）和序列化 tradeoffs 讨论。jobright 聚合亦记录变体 "Implement an LRU Cache. Now, how would you make it persistent?"（讨论 JSON vs pickle 等 tradeoff）。leonstaff 记录另一变体：build LRU Cache, then make it concurrent（线程安全）。这与 Anthropic 'build from scratch + 渐进加需求' 的 coding 风格一致：先正确实现，再层层加约束并讨论取舍。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.tryexponent.com/experiences/anthropic-senior-software-engineer-interview-2ffa5f)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
