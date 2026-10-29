---
id: drustz-5bc8625395eef6f37d
section: forum-notes
order: 17
level: A
title: >-
  Anthropic 面试题库 · 一亩三分地会员版（完整） · Phase 2: Database Schema & Entities (~5
  minutes)
quick: >-
  作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Phase 2: Database Schema & Entities
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
## Phase 2: Database Schema & Entities (~5 minutes)

Before we build APIs, let's decide how to store the data.

### Core Data Structures

```text
User
├── user_id (UUID)
├── username
├── email
├── last_seen_at
└── created_at

Device (To handle phone + laptop)
├── device_id (UUID)
├── user_id
├── device_type (phone, desktop, web)
├── push_token (for notifications)
└── last_active_at

Conversation
├── conversation_id (UUID)
├── participant_1 (user_id)
├── participant_2 (user_id)
├── created_at
└── updated_at (time of last message)
-- Rule: participant_1 is always the smaller ID than participant_2
-- Unique index on (participant_1, participant_2)

Message
├── message_id (UUID)
├── conversation_id
├── sender_id
├── client_message_id (string, unique ID from the phone)
├── content (text)
├── sequence_number (1, 2, 3... per conversation)
└── created_at

MessageStatus (Tracks delivery per device)
├── message_id
├── device_id
├── status (sent, delivered)
└── updated_at
-- Primary key: (message_id, device_id)
```



**Canonical Ordering:** This is a trick to handle 1-to-1 chats. Always store the smaller User ID as `participant_1`. This means "Chat between User A and User B" is the exact same row as "Chat between User B and User A". You can find it with one search.

### Key Decisions

**1. Using Sequence Numbers**

Do not use only timestamps to order messages. Computers have different clocks (clock skew). Instead, use a simple number (1, 2, 3...) for each conversation.

```python
def get_or_create_conversation(user_a, user_b):
    # Sort IDs so we always look up the same pair
    p1, p2 = min(user_a, user_b), max(user_a, user_b)
    return db.upsert(participant_1=p1, participant_2=p2)
```



**2. Tracking Message Status**

We track two different things:

- **Delivered:** This is tracked per **device**. Each phone or laptop says "I got it."
- **Read:** This is tracked per **user**. We save a `last_read_sequence_number`. If the user reads message #50, we know they also read #1 through #49.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
