---
id: drustz-b9adacf07f8f1e4f0e
section: research
order: 66
level: A
title: >-
  System Design: Design ChatGPT (conversational AI backend with SSE token
  streaming)
quick: >-
  supplemental-research-note · System Design: Design ChatGPT (conversational AI
  backend with SSE token streaming)
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
      https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d6f527c4c1bc791ee229e3
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开题面或公开解法。

Stage: Onsite. Design the backend for a ChatGPT-like service: multi-turn conversations, durable history (resume days later), context assembly, GPU-cluster inference dispatch, token streaming via Server-Sent Events. Given targets: TTFT <=500ms p50 / 2s p95; durable conversation persistence. Full doc structure: clarifying Q&A (6 items with interviewer answers + takeaways), functional/non-functional requirements, back-of-envelope estimation, data model + access patterns + storage tradeoff, API design (send-message + SSE event contract + history fetch), high-level architecture, chat completion flow, TTFT budget breakdown, admission control and caching, deep dives (GPU inference scheduling and CONTINUOUS BATCHING; context window management and token budget assembly; streaming delivery contract and failure/reconnect recovery), other considerations (safety guardrails pipeline latency budget, multi-model routing and gradual rollout, conversation summarization for extended context, cost management and tier-based throttling), and explicit interviewer expectations broken down by Junior/Intermediate/Senior level.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/system-design/69d6f527c4c1bc791ee229e3)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。
