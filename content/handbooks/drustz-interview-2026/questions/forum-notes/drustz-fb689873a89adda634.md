---
id: drustz-fb689873a89adda634
section: forum-notes
order: 16
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Phase 1: Define the Goals (~5 minutes)'
quick: >-
  作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Phase 1: Define the Goals (~5
  minutes)
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
## Phase 1: Define the Goals (~5 minutes)

A 1-to-1 chat system is smaller than WhatsApp or Slack. We need to define exactly what to build so we don't waste time on features we don't need.

### User Features

Describe these as things the user can do:

- **Send messages:** Users can send text to another user.
- **Receive messages:** Users get messages almost instantly if they are online.
- **Conversation history:** Users can see old messages.
- **Read receipts:** The sender knows when the other person has read the message.
- **Offline delivery:** If a user is offline, the message waits until they come back online.
Stick to these 4-5 main features. We do not need group admins or channels.

### Technical Requirements

| Requirement | Target | Reason |
| --- | --- | --- |
| **Scale** | 100M DAU, 1B messages/day | A medium-sized system. |
| **Latency** | < 500ms delivery | Needs to feel instant. |
| **Availability** | 99.9%+ | Users expect chat to always work. |
| **Ordering** | Strict order | "Hello" then "How are you?" must not swap. |
| **Durability** | No data loss | We must never lose a sent message. |

**Key Questions to Ask:**

- "What matters more: availability (always working) or consistency (perfect order)?" — *Answer:* Messages must be in order, even if it takes a tiny bit longer.
- "How long do we keep messages?" — *Answer:* Forever (unless we change it for privacy).
- "Do users have multiple devices?" — *Answer:* Yes, a user might use a phone and a laptop.

### Math & Estimations

Let's do some quick math to see how big our servers need to be:

```text
Users:
- Daily Active Users (DAU): 100 million
- Messages per user per day: 10
- Total messages per day: 1 billion

Traffic Load:
- Average messages per second: 1B / 86,400 ≈ 11,500 QPS
- Peak time (busy hours): ~35,000 QPS

Connections:
- Users online at the same time: 10% of DAU = 10M WebSocket connections

Storage:
- Size of one message: 200 bytes
- Storage per day: 200 GB
- Storage per year: ~73 TB
```



With 35,000 QPS and 10 million open connections, we need a distributed system. One server is not enough. We need many servers working together.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
