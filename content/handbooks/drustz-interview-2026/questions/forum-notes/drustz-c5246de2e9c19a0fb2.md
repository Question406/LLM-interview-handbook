---
id: drustz-c5246de2e9c19a0fb2
section: forum-notes
order: 86
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 5: Architecture Overview'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Step 5: Architecture Overview'
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
## Step 5: Architecture Overview

Here is how the different parts of the system connect.

### Component Diagram

- **Client (Browser):**

Uses **Monaco Editor** (like VS Code) to handle large text files smoothly.
- Uses **IndexedDB** to save drafts on your computer so you don't lose work if internet fails.
- **Load Balancer:**

Sends traffic to the API servers.
- **API Servers (Node.js):**

Handles requests.
- Checks if the user is allowed (Auth).
- Connects to WebSockets.
- **Redis (Cache):**

Stores recent prompts for speed.
- Counts requests to limit usage (Rate Limiting).
- **PostgreSQL (Database):**

Stores user data and small prompts.
- **S3 (File Storage):**

Stores huge prompts (over 100KB).
- **Bull Queue:**

A waiting list for jobs. If many people click "Run" at once, this puts them in line.
- **LLM API:**

External services like OpenAI or Anthropic.

### How Data Moves (The Flow)

**When a User Clicks "Run":**

- Browser sends a WebSocket message: "Run this prompt."
- Server checks: "Is the prompt too long for this model?"
- Server puts the job in the **Bull Queue**.
- A background worker picks up the job and calls the LLM API.
- As the API sends text back, the worker streams it to the Browser via WebSocket.
- When finished, the result is saved to the Database.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
