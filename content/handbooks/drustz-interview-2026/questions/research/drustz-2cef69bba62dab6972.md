---
id: drustz-2cef69bba62dab6972
section: research
order: 104
level: A
title: System design 真题：1B 文档 1M QPS 分布式搜索系统
quick: supplemental-research-note · System design 真题：1B 文档 1M QPS 分布式搜索系统
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
      https://medium.com/@anqi.silvia/my-2025-anthropic-software-engineer-interview-experience-9fc15cd81a99
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

Medium 上 2025 年 SWE 候选人面经：system design 轮为设计 distributed search system，规格 1B documents、1M QPS，需要处理 sharding、caching、LLM inference scaling；面试官重点追问避免 hotspot 和 GPU 显存优化。其他被报告的 system design 题（jobright 聚合）：分布式 job queue（类 Kafka + workers）、"Implement a GPU Scheduling System Using Credits"（抢占逻辑、防资源垄断、容错）、"Design a 1-on-1 Chat System"（SQL vs Cassandra、离线投递、消息顺序、WebSocket 扩展）、为开发者设计访问 Anthropic 模型的 API。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://medium.com/@anqi.silvia/my-2025-anthropic-software-engineer-interview-experience-9fc15cd81a99)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
