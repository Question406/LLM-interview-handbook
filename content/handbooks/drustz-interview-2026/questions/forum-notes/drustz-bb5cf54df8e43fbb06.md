---
id: drustz-bb5cf54df8e43fbb06
section: forum-notes
order: 18
level: A
title: >-
  Anthropic 面试题库 · 一亩三分地会员版（完整） · Phase 3: How Client and Server Talk (~5
  minutes)
quick: >-
  作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Phase 3: How Client and Server Talk
  (~5 minutes)
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
## Phase 3: How Client and Server Talk (~5 minutes)

We need **bidirectional** communication (two-way talking). The server must be able to push a message to the client without the client asking for it.

### Why WebSockets?

| Protocol | How it works | Best For |
| --- | --- | --- |
| **HTTP** | Client asks, Server answers | Loading web pages |
| **WebSocket** | Connection stays open | Chat, Games |
| **Server-Sent Events** | Server talks, Client listens | News Tickers |

For chat, both sides talk. WebSockets are the best choice because they keep a single line open.

### JSON Commands

**Client sends to Server:**

```text
// Send a message
{
  "action": "send_message",
  "conversation_id": "conv_123",
  "content": "Hello!",
  "client_message_id": "local_456"  // Unique ID to prevent duplicates
}

// Tell server I read messages
{
  "action": "read_receipt",
  "conversation_id": "conv_123",
  "last_read_sequence": 42
}

// Keep connection alive
{ "action": "ping" }
```



**Server sends to Client:**

```text
// Incoming message
{
  "event": "new_message",
  "message_id": "msg_789",
  "conversation_id": "conv_123",
  "sender_id": "user_456",
  "content": "Hello!",
  "sequence_number": 42,
  "timestamp": "2024-01-15T10:30:00Z"
}

// Confirm message reached the other person
{
  "event": "delivered",
  "message_id": "msg_789",
  "conversation_id": "conv_123",
  "timestamp": "2024-01-15T10:30:01Z"
}

// Other person read your message
{
  "event": "read",
  "conversation_id": "conv_123",
  "reader_id": "user_456",
  "last_read_sequence": 42
}
```



**Note on `client_message_id`:** This is for **Idempotency**. If the internet cuts out while sending, the app might retry sending the same message. The server checks this ID. If it has seen it before, it ignores the duplicate.

### Standard HTTP API (REST)

Some things don't need WebSockets. We can use standard HTTP for them:

```http
// Load list of chats
GET /conversations?cursor=...&limit=20

// Load old messages (scrolling up)
GET /conversations/{id}/messages?before_sequence=12345&limit=50

// Start talking to someone new
POST /conversations
Request: { "recipient_user_id": "..." }
```

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
