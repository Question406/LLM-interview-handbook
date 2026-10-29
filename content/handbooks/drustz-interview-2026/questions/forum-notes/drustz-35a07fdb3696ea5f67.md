---
id: drustz-35a07fdb3696ea5f67
section: forum-notes
order: 112
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 5: System Architecture'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 5: System Architecture'
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
## Step 5: System Architecture

### The Diagram

Imagine a long line of people passing buckets of water.

- **External Storage (S3):** The water source.
- **Coordinator:** The person shouting directions.
- **Workers (W1, W2, ... W100):** The people passing buckets.
**Flow:**
`S3` --> `W1` --> `W2` --> `W3` ... --> `W100`

### How It Works (The Phases)

**Phase 1: Setup**
The Coordinator chops the file list into 500 pieces (1GB each). It tells the workers: "Get ready. W1 gives to W2, W2 gives to W3..."

**Phase 2: Seeding**
Worker 1 (W1) downloads "Chunk 0" from S3.
As soon as W1 has Chunk 0, it sends it to W2.
At the same time, W1 downloads Chunk 1 from S3.

**Phase 3: The Pipeline**
Everyone is busy.

- W1 is downloading from S3 and sending to W2.
- W2 is receiving from W1 and sending to W3.
- This happens for all 500 chunks.
**Phase 4: Finish**
Workers verify the files using checksums. They tell the Coordinator "Success".

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
