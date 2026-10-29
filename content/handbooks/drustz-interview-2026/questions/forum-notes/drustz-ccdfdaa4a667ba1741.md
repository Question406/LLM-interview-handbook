---
id: drustz-ccdfdaa4a667ba1741
section: forum-notes
order: 143
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 1: Clarifying the Requirements'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 1: Clarifying the Requirements'
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
## Step 1: Clarifying the Requirements

First, ask questions to understand exactly what you need to build.

### Questions to Ask

**Traffic and Speed:**

- "How many requests per second (RPS) do we expect?"

*Why ask:* This tells us if we need a simple setup or a complex distributed system.
- "What is the allowed Latency?" (e.g., 500ms).

*Why ask:* This helps us decide how long we can wait to fill a batch.
**Hardware:**

- "How many GPUs can we start with?"
- "Is the GPU function reliable, or does it crash often?"
**The Problem Details:**

- "Does the 100ms processing time change if the batch is small?" (Answer: No, it is fixed).
- "Do we need to let users cancel requests?" (Answer: No).

### Summary of What We Are Building

**What it does:**

- Takes single string inputs via HTTP POST.
- Users wait for the answer (Synchronous).
- Groups 1-100 requests into a batch.
- Sends batch to the `batchstring()` function.
- Returns the correct answer to the user.
- Handles high traffic (1000+ RPS).
**Performance Goals:**

- **Latency:** P95 < 500ms.
- **Uptime:** 99.9%.
- **Efficiency:** Use GPUs well (aim for 70-80% usage).

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
