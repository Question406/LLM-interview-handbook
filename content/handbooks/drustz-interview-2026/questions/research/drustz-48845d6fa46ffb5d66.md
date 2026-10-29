---
id: drustz-48845d6fa46ffb5d66
section: research
order: 69
level: A
title: 'System Design: GPU Scheduling Platform (shared training/batch-job cluster)'
quick: >-
  supplemental-research-note · System Design: GPU Scheduling Platform (shared
  training/batch-job cluster)
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
      https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d71cbfc4c1bc791ee22b22
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开预览与可核实要点。

Stage: Onsite. Scheduling + execution layer for a shared GPU cluster: users submit containerized batch jobs (ML training, fine-tuning, batch inference) with resource requirements and priority; platform queues by priority, places on nodes with capacity, runs in containers, monitors, auto-handles failures. Preview clarifying Q&A: each job fits on a single node (gang scheduling for distributed training explicitly deferred to follow-up); node can become unreachable between placement decision and job start - every placement is a distributed commitment across scheduler, database, and remote node agent, any of which can fail mid-assignment. Full solution paywalled.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d71cbfc4c1bc791ee22b22)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
