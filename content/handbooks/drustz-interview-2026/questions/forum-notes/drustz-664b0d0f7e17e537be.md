---
id: drustz-664b0d0f7e17e537be
section: forum-notes
order: 71
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 5: System Overview'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 5: System Overview'
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Step 5: System Overview

The system has 6 main parts. Here is how they fit together.

### Architecture Diagram

```text
┌─────────────┐
│   Clients   │
└──────┬──────┘
       │ (sync HTTP request)
       v
┌─────────────────┐
│  Load Balancer  │
└──────┬──────────┘
       │
       v
┌──────────────────────┐◀──────────┐
│  Rate Limiter/       │           │ Feedback: Tells Gateway if GPUs are full
│  API Gateway         │           │ 
└──────┬───────────────┘           │
       │ (write to queue)          │
       v                           │
┌─────────────────────┐            │
│  Message Queue(s)   │            │
│  (one per tier)     │            │
│  - Free tier queue  │            │
│  - Paid tier queue  │            │
│  - Enterprise queue │            │
└──────┬──────────────┘            │
       │ (poll/consume)            │
       v                           │
┌──────────────────────┐           │
│  Request Batcher     │           │
│  (Batching Service)  │           │
│  - Groups requests   │           │
│  - Manage timeouts   │───────────┘
└──────┬───────────────┘
       │ (batched requests)
       v
┌──────────────────────┐
│   GPU Worker Pool    │
│  - Load balancer     │
│  - Multiple GPU pods │
└──────┬───────────────┘
       │ (batched responses)
       v
┌──────────────────────┐
│  Response Handler    │
│  (maps back to       │
│   original requests) │
└──────┬───────────────┘
       │
       v
    (return to client)
```



### What Each Part Does

**1. Load Balancer**

- Spreads traffic across different API Gateways.
- Handles secure connections (SSL).
**2. Rate Limiter / API Gateway**

- Checks API keys.
- Limits usage based on user tier.
- Sends requests to the correct queue.
- Keeps the connection open so the client gets an answer.
**3. Message Queues (Redis)**

- Separate queues for Free, Paid, and Enterprise users.
- Keeps requests organized.
- Acts as a buffer if the GPUs are busy.
**4. Request Batcher**

- Pulls requests from the queue.
- Groups them into a batch (e.g., wait for 32 requests OR 40ms time limit).
- Sends batches to GPUs.
**5. GPU Worker Pool**

- The actual servers doing the AI work.
- Processes the batch and returns results.
**6. Response Handler**

- Takes the batch result and breaks it back into individual answers.
- Matches answers to the waiting clients.

### How a Request Moves Through the System

- **Client → Load Balancer**: Client sends a request.
- **API Gateway**: Checks if the user is allowed (Paid user). Puts the request in the "Paid Queue" and keeps the connection open.
- **Queue**: The request waits here. (Average wait: ~20ms).
- **Batcher**: Picks up the request, waits a few milliseconds to find other requests, groups them, and sends them to a GPU.
- **GPU**: Processes the whole batch (takes ~50ms).
- **Response**: The system separates the answers and sends yours back to you.
**Total Time: ~91-131ms** (Much faster than the 500ms limit).

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
