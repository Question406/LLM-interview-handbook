---
id: drustz-f2b0beab15095cb783
section: forum-notes
order: 74
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Extra Discussion Points
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Extra Discussion Points
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
## Extra Discussion Points

### Option A: Using a Queue (Recommended)

**Queue sits BEFORE the Batcher.**

- **Why:** If the Batcher crashes, the request is safe in the queue (Redis/Kafka).
- **Benefit:** Keeps Paid and Free users separated easily.

### Option B: Fast but Risky (In-Memory)

**Batching happens inside the API Gateway memory.**

- **Why:** It's faster (no queue hop).
- **Risk:** If the server crashes, you lose the requests.
- **Use Case:** Only if speed is the *only* thing that matters.

### Decision: Saving Requests to Disk vs Memory

- **Kafka (Disk):** Safe. No data loss. Slower.
- **Redis/Memory:** Fast. Some risk of data loss on crash.
- **Verdict:** For this problem, **Redis** is usually best because we need low latency, but **Kafka** is better if these are financial/critical transactions.

### Queue Length

- **Normal:** The queue should be almost empty (0-30 requests).
- **Bad:** If the queue grows > 500, the system is failing.

### GPU Utilization Target

- **Target:** 70-80%.
- **Why not 100%?** If you run at 100%, any tiny spike creates a massive queue instantly. You need "headroom" to absorb bumps in traffic.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
