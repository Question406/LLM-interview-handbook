---
id: drustz-dd0268a2fbaea2b6ef
section: research
order: 102
level: A
title: Anthropic 近期系统设计题库汇总（辅导教练整理）：Claude chat service、分布式/混合搜索、p95 延迟排查、1B 文档爬虫管线
quick: >-
  supplemental-research-note · Anthropic 近期系统设计题库汇总（辅导教练整理）：Claude chat
  service、分布式/混合搜索、p95 延迟排查、1B 文档爬虫管线
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
      https://www.reddit.com/r/InterviewCoderHQ/comments/1rxinyi/targeting_anthropic_insights_from_recent/
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

InterviewCoderHQ 'Targeting Anthropic' 帖（drCounterIntuitive，面试教练，2026-03）汇总近期 loop 真题：(1) Design a Claude chat service；(2) Design a distributed search system；(3) Design a hybrid search system（关键词+向量）；(4) Debug performance degradation：p95 延迟从 100ms 飙到 2000ms，如何排查、建监控、排序修复优先级；(5) Design data pipeline with concurrent web crawler for ~1B documents。风格提醒：interviewer-driven、time-box、中途 pivot，可能不让你按'需求→估算→API→高层→深挖'模板走；另确认 reference check 可能在流程走完前就开始；并发题常态化；表现好也可能不发 offer（决策不透明）。senior 还有 technical presentation 轮（讲自己项目）。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.reddit.com/r/InterviewCoderHQ/comments/1rxinyi/targeting_anthropic_insights_from_recent/)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
