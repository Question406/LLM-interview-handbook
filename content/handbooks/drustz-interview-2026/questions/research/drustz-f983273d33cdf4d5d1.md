---
id: drustz-f983273d33cdf4d5d1
section: research
order: 60
level: A
title: >-
  Design a GPU inference batching system (Anthropic's most-reported system
  design question)
quick: >-
  supplemental-research-note · Design a GPU inference batching system
  (Anthropic's most-reported system design question)
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
    url: 'https://www.tryexponent.com/blog/anthropic-system-design-interview'
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

Prompt: 'You have a single GPU that can process up to 100 inputs per batch. Users submit requests synchronously and wait for results. Design the system that receives inputs, batches them, processes them on the GPU, and returns responses to the correct users.' Extension version: end-to-end LLM query batching — request intake, batching policy, GPU routing, load balancing, response delivery. Follow-ups: how do you determine GPU capacity; failover handling; what happens when a batch member fails; queueing vs latency trade-off. Asked in the 50-55 min phone screen and/or onsite (4-5 rounds, 45-55 min each). Exponent notes Anthropic questions 'use AI framing but test classic distributed systems infrastructure' and staff candidates must drive the conversation. Same question appears in Exponent's question bank tagged Anthropic + 7 other companies.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.tryexponent.com/blog/anthropic-system-design-interview)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
