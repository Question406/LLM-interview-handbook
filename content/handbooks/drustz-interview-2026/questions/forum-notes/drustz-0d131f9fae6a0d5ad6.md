---
id: drustz-0d131f9fae6a0d5ad6
section: forum-notes
order: 88
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 7: Fixing Performance Issues'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 7: Fixing Performance Issues'
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
## Step 7: Fixing Performance Issues

Identifying where the system might break.

- **Cost of LLM API:**

*Risk:* Users running the same prompt over and over cost us money.
- *Fix:* **Cache responses.** If the prompt + model + settings are identical, return the saved answer from the last run.
- **Latency (Slowness):**

*Risk:* Loading a 10MB prompt from S3 takes time.
- *Fix:* Use a CDN (Content Delivery Network) or cache active prompts in Redis.
- **Rate Limits:**

*Risk:* OpenAI blocks us because we send too many requests.
- *Fix:* Use the **Queue**. If we hit the limit, hold the jobs in the queue and retry them later.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
