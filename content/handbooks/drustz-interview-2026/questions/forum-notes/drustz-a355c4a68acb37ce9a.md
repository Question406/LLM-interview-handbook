---
id: drustz-a355c4a68acb37ce9a
section: forum-notes
order: 144
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 2: Estimating Scale and Resources'
quick: >-
  作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 2: Estimating Scale and
  Resources
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
## Step 2: Estimating Scale and Resources

We need to do some math to guess how many GPUs we need.

### Assumptions

- **Traffic:** 1000 requests per second (RPS).
- **Batch Size:** We aim for 32 requests per batch.
- **GPU Speed:** 100ms per batch.
- **Timeout:** We wait 50ms max to fill a batch.

### The Math

**How many GPUs do we need?**

- **Throughput per GPU:**

1 batch takes 100ms.
- In 1 second (1000ms), a GPU can run 10 batches.
- Each batch has 32 requests.
- So, 1 GPU handles: 10 batches × 32 requests = 320 requests per second.
- **Total GPUs needed:**

We have 1000 RPS.
- 1000 / 320 = 3.125 GPUs.
- Round up to **4 GPUs**.
- **Add Safety Buffer:**

We don't want to run at 100% capacity. Let's aim for 70%.
- 4 GPUs / 0.7 ≈ 5.7.
- **Final count: 6 GPUs.**
**How long will users wait (Latency)?**

- **Waiting for batch:** 0ms to 50ms. Average is ~15-25ms.
- **Network travel:** ~10ms.
- **GPU time:** 100ms (fixed).
- **Total Average:** 25 + 10 + 100 = **135ms**.
- This is good. It is well under the 500ms limit.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
