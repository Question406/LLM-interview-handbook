---
id: drustz-f3277fb64fdc408ace
section: forum-notes
order: 149
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 7: Fixing Potential Problems'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 7: Fixing Potential Problems'
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
## Step 7: Fixing Potential Problems

A good design must handle failures.

### Problem 1: GPU Crashes

**Scenario:** A GPU crashes while processing a batch of 32 requests.
**Solution:**

- The Batching Service should detect the error.
- It can retry the batch on a different GPU.
- If it fails again, return a `500 Error` to the users so they know to try again.

### Problem 2: Single Point of Failure

**Scenario:** If the Redis Queue dies, the whole system stops.
**Solution:**

- Use Redis Cluster (multiple Redis nodes).
- If the main node dies, a backup node takes over automatically.

### Problem 3: Low Traffic Inefficiency

**Scenario:** At night, only 1 request comes every second.
**Problem:** The GPU waits 50ms, processes 1 item, then sits idle. This wastes money.
**Solution:**

- Use **Auto-scaling**.
- Detect low traffic and turn off 5 of the 6 GPUs.
- Spin them back up when traffic increases in the morning.

### Monitoring

You need dashboards to watch the system health.

- **Critical Alert:** If Queue size > 1000 (System is backed up).
- **Critical Alert:** If Latency > 500ms (System is too slow).
- **Warning:** If GPU usage > 85% (Need to add more GPUs soon).

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100012*)

---

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
