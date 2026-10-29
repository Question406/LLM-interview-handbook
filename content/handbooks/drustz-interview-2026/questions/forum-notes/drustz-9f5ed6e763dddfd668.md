---
id: drustz-9f5ed6e763dddfd668
section: forum-notes
order: 145
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 3: API Design'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 3: API Design'
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
## Step 3: API Design

This defines how users talk to our system and how our internal servers talk to each other.

### User API (Public)

**Request:**

```text
POST /api/inference
Content-Type: application/json

{
  "input": "E equals "
}
```



**Response:**

```json
{
  "output": "E equals mc^2",
  "latency_ms": 145,
  "request_id": "req_abc123"
}
```



### Internal API (Batcher to GPU)

**Request:**

```text
{
  "batch_id": "batch_xyz",
  "inputs": ["E equals ", "Q: What is ", ...],
  "request_ids": ["req_1", "req_2", ...],
  "return_to": "api-instance-1"
}
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
