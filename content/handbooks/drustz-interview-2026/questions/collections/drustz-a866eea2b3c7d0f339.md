---
id: drustz-a866eea2b3c7d0f339
section: collections
order: 50
level: A
title: 通用 ML 理论 + ML System Design 资源库 · System Design
quick: 作者文档章节 · 通用 ML 理论 + ML System Design 资源库 · System Design
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/theory-and-mlsd.md
    type: primary
---
## System Design

### AI-framed vs classic system design blend reported in 2025-2026 loops (System Design Handbook questions blog)
*medium · 频率: prep compilation · 2026*

Three archetypes with answer skeletons: (1) recommendation engine for e-commerce/streaming — batch vs real-time personalization, data pipeline + feature store + training service + model registry + inference service, cold start, CTR + drift monitoring; (2) real-time fraud detection — millisecond transaction analysis, Kafka/PubSub streaming ingestion, ensemble models + rules, tight feature-extraction latency budgets, fallbacks, feedback loops from confirmed fraud; (3) LLM-powered chat system — third-party API vs self-hosted decision, prompt orchestration, caching, rate limiting, GPU allocation/autoscaling if self-hosted, RAG, token limits + context-window management, cost monitoring, moderation layers. Site's overall 2026 thesis (echoed by Exponent): 'design a system that serves an LLM' has moved from ML-engineer-only loops into general SWE loops, and evaluation methodology is 'the new system design' — interviewers weight cost, latency, guardrails, monitoring over the architecture diagram.

来源: &lt;[来源链接](https://www.systemdesignhandbook.com/blog/ai-system-design-interview-questions/&gt;)

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/theory-and-mlsd.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/theory-and-mlsd.md)。作者整理资料；许可和第三方来源范围见阅读指南。
