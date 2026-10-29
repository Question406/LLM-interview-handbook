---
id: drustz-cbeb00fad72823bb4f
section: forum-notes
order: 114
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 7: Fixing Bottlenecks'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 7: Fixing Bottlenecks'
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
## Step 7: Fixing Bottlenecks

### 1. External Bandwidth

**Problem:** The download from S3 is only 10 Gbps.
**Solution:** Only the first worker (W1) downloads from S3. Everyone else gets data from W1 via the local network. This saves the internet connection.

### 2. Disk Speed

**Problem:** Writing 500GB quickly can be too fast for hard drives.
**Solution:** Use NVMe SSDs (very fast disks). Write data in parallel streams.

### 3. Coordinator Overload

**Problem:** If 10,000 workers send updates constantly, the Coordinator will crash.
**Solution:**

- Workers only send updates every 10 chunks (batching).
- Use multiple Coordinators (one leader, several backups).

### 4. Corruption

**Problem:** Bits get flipped during transfer. The file is broken.
**Solution:**

- Calculate the SHA256 Hash of every chunk.
- If the hash doesn't match, ask for that chunk again.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
