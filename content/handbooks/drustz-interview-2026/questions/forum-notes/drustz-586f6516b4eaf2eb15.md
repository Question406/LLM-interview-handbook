---
id: drustz-586f6516b4eaf2eb15
section: forum-notes
order: 70
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 4: Database and Data Structure'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 4: Database and Data Structure'
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
## Step 4: Database and Data Structure

This section defines how we store data and move it around.

### Data Objects

**Request Queue (Message Queue - Redis/Kafka):**

```text
{
  "request_id": "req_abc123",
  "user_id": "user_456",
  "tier": "paid",           // free, paid, enterprise
  "model": "gpt-4",
  "input": "...",
  "parameters": {...},
  "timestamp": "2024-01-15T10:30:00Z",
  "timeout": "2024-01-15T10:30:05Z"  // 5 second timeout
}
```



**Batch Info (Inside the Batcher):**

```python
{
    "batch_id": "batch_xyz789",
    "requests": ["req_1", "req_2", ..., "req_32"],
    "created_at": "2024-01-15T10:30:00.100Z",
    "sent_to_gpu": "2024-01-15T10:30:00.150Z",
    "gpu_worker_id": "gpu-worker-3",
}
```



**Request Database (PostgreSQL/Redis):**

```sql
-- Main table for history (PostgreSQL)
CREATE TABLE requests (
  request_id VARCHAR(50) PRIMARY KEY,
  user_id VARCHAR(50),
  model VARCHAR(50),
  status VARCHAR(20),  -- queued, processing, completed, failed
  created_at TIMESTAMP,
  completed_at TIMESTAMP,
  latency_ms INTEGER,
  tokens_used INTEGER
);

-- Fast lookup for active requests (Redis)
{
  "req_abc123": {
    "status": "processing",
    "batch_id": "batch_xyz789",
    "client_connection_id": "conn_123"  // To send the answer back
  }
}
```



**GPU List (Redis):**

```text
{
  "gpu-worker-1": {
    "status": "healthy",
    "current_utilization": 0.78,
    "requests_processed": 15234,
    "last_heartbeat": "2024-01-15T10:30:05Z"
  },
  "gpu-worker-2": {...},
  ...
}
```



### Choosing the Database

**Redis (In-Memory):**

- Use this for Queues, Live Tracking, and Rate Limits.
- **Why:** It is extremely fast (<1ms) and handles many requests.
**PostgreSQL (Permanent Storage):**

- Use this for History, User Info, and Logs.
- **Why:** It is reliable (ACID) and good for complex searches.
**Kafka (Queue Alternative):**

- Use this if you absolutely cannot lose a message if a server crashes.
- **Trade-off:** It is slower than Redis (~5-20ms vs ~1ms). For this problem, Redis is better because speed is critical.

### Indexing

```sql
-- Make searching faster
CREATE INDEX idx_requests_user_id ON requests(user_id, created_at DESC);
CREATE INDEX idx_requests_status ON requests(status) WHERE status IN ('queued', 'processing');
CREATE INDEX idx_requests_created_at ON requests(created_at DESC);
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
