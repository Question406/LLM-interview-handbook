---
id: drustz-a4185c4352fddeabd1
section: forum-notes
order: 83
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 2: Estimating Scale and Costs'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 2: Estimating Scale and Costs'
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
## Step 2: Estimating Scale and Costs

Let's do some math to see how big the system needs to be.

### Assumptions

- **Users:** 1 million total users.
- **Daily Usage:** 10,000 users per day.
- **Prompt Size:** Most are small (1KB), but some are huge (10MB).
- **Read vs Write:** Users read/view prompts much more than they save them (80% read, 20% write).

### Calculations

**Traffic:**

- Reads: ~0.6 requests per second (very low).
- Writes: ~0.12 requests per second (very low).
- **Conclusion:** Traffic is low. We don't need complex database sharding yet.
**Storage:**

- Prompts: 1M users × 10 prompts × 1KB = 10GB.
- Versions: If we save every version, it gets big (300GB).
- **Conclusion:** Storage is cheap. We can use S3 for big files and a database for small ones.
**Costs:**

- **LLM API Cost:** This is the most expensive part.
- If we use high-end models (like Claude 3.5 Sonnet), it could cost &#36;450/day.
- **Strategy:** We must use **Caching** to save money. If a user runs the exact same prompt twice, show the saved result instead of paying the API again.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
