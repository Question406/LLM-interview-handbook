---
id: drustz-aaffb9cbeb6f6b1dc6
section: forum-notes
order: 204
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · 3. How Clients Talk to Servers (API)
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · 3. How Clients Talk to Servers (API)
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## 3. How Clients Talk to Servers (API)

### Protocol Strategy

| Action | Protocol | Why? |
| :--- | :--- | :--- |
| **Manage Files/Settings** | REST | Simple and standard. |
| **Terminal Output** | WebSocket | Needs to be real-time (two-way). |
| **File Uploads** | REST + multipart | Better for large data. |

### REST Endpoints

```text
# Workspace Basics
POST   /api/workspaces                   # Create new
GET    /api/workspaces/{id}              # Get details
DELETE /api/workspaces/{id}              # Delete

# Files
GET    /api/workspaces/{id}/files        # List all files
GET    /api/files/{id}                   # Read file content
POST   /api/workspaces/{id}/files        # Create file
PUT    /api/files/{id}                   # Save file content

# Running Code
POST   /api/workspaces/{id}/run          # Run a command
# Returns: { "process_id": "...", "stream_token": "..." }

POST   /api/processes/{id}/cancel        # Stop a command
```



### WebSocket Protocol

We use WebSockets to stream the terminal text. The client gets a `stream_token` from the REST API first.

**Connect:**
`WSS /api/stream/{sandbox_id}?token=stream_token`

**Server sends to Client:**

```json
{
  "type": "output",
  "process_id": "proc-123",
  "stream": "stdout",
  "data": "Hello World\n"
}
```



**Client sends to Server:**

```json
{
  "type": "input",
  "process_id": "proc-123",
  "data": "user typed something\n"
}
```



The WebSocket connects to the **Sandbox**, not just one process. This lets us run two commands at once (like a server and a test runner) over one connection.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
