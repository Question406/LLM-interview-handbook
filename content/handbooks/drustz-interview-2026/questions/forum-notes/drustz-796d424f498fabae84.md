---
id: drustz-796d424f498fabae84
section: forum-notes
order: 146
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 4: Data Storage'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 4: Data Storage'
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
## Step 4: Data Storage

We need to decide how to store data in memory and in the database.

### 1. In-Memory (API Server)

The API server needs to remember who is waiting for an answer.

```text
# Map request IDs to the open user connection
pending_requests = {
  "req_abc123": <HTTP connection object>,
  "req_def456": <HTTP connection object>
}
```



### 2. Redis (Shared Storage)

We use Redis to pass messages between servers.

**Request Queue:**
A list where API servers put new requests.

```python
Key: "batch_queue"
Value: ['{"request_id": "req_1", "input": "...", "return_to": "api-1"}', ...]
```



**Response Channels (Pub/Sub):**
Channels to send answers back to the specific API server that asked.

```python
Channel: "responses:api-instance-1"
Channel: "responses:api-instance-2"
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
