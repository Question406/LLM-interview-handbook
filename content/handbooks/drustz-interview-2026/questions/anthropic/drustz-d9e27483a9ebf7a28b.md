---
id: drustz-d9e27483a9ebf7a28b
section: anthropic
order: 27
level: A
title: SD Q4 1To1 Chat System
quick: locally-saved-topic-editorial · SD Q4 1To1 Chat System
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/sd-q4-1to1-chat-system
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Design a 1-to-1 Chat System

### Design a 1-to-1 Chat System

Design a chat system that supports **only 1-to-1 messaging** between users. Group chats, channels, and other multi-party features are not included.

Interviewers often ask deep questions about how things work under the hood. Do not just guess. You must explain the "how" behind the "what." If you suggest WebSockets, be ready to explain how connections stay open. If you talk about message order, be ready to explain how time works in distributed systems.

**Disclaimer:** This is a sample solution. To prepare best, try to solve the problem yourself first. System design questions are open-ended, and there are many right answers.

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



## Phase 4: System Architecture (~15-25 minutes)

This is the main part of the interview. We need to draw how the pieces fit together.

### The Components

| Component | Job |
| --- | --- |
| **Load Balancer (L4)** | Spreads incoming connections to different servers. |
| **WebSocket Servers** | Holds the open connection to the user's phone/laptop. |
| **Message Service** | The brain. Handles logic, saves messages, assigns numbers. |
| **PostgreSQL** | Long-term storage for all data. |
| **Redis Cluster** | Fast memory storage. Used for routing messages and temporary queues. |

### Life of a Message (The Flow)

Imagine User A sends a message to User B:

- User A sends the message to their **WebSocket Server**.
- The server passes it to the **Message Service**.
- The service saves the message in **PostgreSQL** and gives it a sequence number.
- The service publishes the message to **Redis Pub/Sub**.
- User B's WebSocket Server receives the notification from Redis.
- User B's server pushes the message to User B's phone.
- User B's phone sends an "ACK" (acknowledgment) saying "I got it."
We use an **in-flight queue**. We put the message in a temporary list. We only remove it once the user confirms they received it. This makes sure messages don't get lost.

### The Routing Problem

We have many WebSocket servers. Server 1 has User A. Server 2 has User B. How does Server 1 send data to Server 2?

**Solution: Pub/Sub (Publish/Subscribe)**

We use Redis Pub/Sub. Every WebSocket server "subscribes" to the users connected to it.

- When User B connects to Server 2, Server 2 subscribes to channel `user:B`.
- To send to User B, we just "publish" the message to channel `user:B`.
- Redis ensures Server 2 gets that data. Server 2 then sends it to the real user.
This is better than keeping a giant list of "Who is on which server" because lists get messy if servers crash.

### Handling Offline Users

If User B is offline:

- The message stays in the database (Inbox).
- It sits in a pending queue.
- When User B comes online, they ask the server: "What is the last message I have?"
- The server sends everything that came after that number.

### Detailed Database SQL

```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    last_seen_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Devices table (for multiple logins)
CREATE TABLE devices (
    device_id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users,
    device_type VARCHAR(20) NOT NULL,
    push_token VARCHAR(255),
    last_active_at TIMESTAMP DEFAULT NOW()
);

-- Conversations
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY,
    participant_1 UUID NOT NULL REFERENCES users,
    participant_2 UUID NOT NULL REFERENCES users,
    created_at TIMESTAMP DEFAULT NOW(),
    -- Enforce canonical ordering
    CONSTRAINT participant_order CHECK (participant_1 < participant_2),
    UNIQUE (participant_1, participant_2)
);

-- Messages
CREATE TABLE messages (
    message_id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations,
    sender_id UUID NOT NULL REFERENCES users,
    client_message_id VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    sequence_number BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (conversation_id, sequence_number),
    UNIQUE (conversation_id, sender_id, client_message_id)
);

-- Tracking if a message reached a device
CREATE TABLE message_status (
    message_id UUID NOT NULL REFERENCES messages,
    device_id UUID NOT NULL REFERENCES devices,
    status VARCHAR(20) NOT NULL DEFAULT 'sent',
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (message_id, device_id)
);

-- Read Receipts (The highest number read)
CREATE TABLE read_receipts (
    user_id UUID NOT NULL REFERENCES users,
    conversation_id UUID NOT NULL REFERENCES conversations,
    last_read_sequence BIGINT NOT NULL DEFAULT 0,
    last_read_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, conversation_id)
);
```



### Sharding (Splitting Data)

We have too much data for one database. We need to split it (Shard).

We shard by **`conversation_id`**.

- All messages for Chat 123 go to Database A.
- All messages for Chat 456 go to Database B.
This makes loading chat history very fast because all messages for one chat are in the same place.

## Phase 5: Handling Scale & Challenges (~15-20 minutes)

Now we look at the hard problems.

### Problem 1: Message Ordering

How do we make sure User A and User B see messages in the exact same order?

**Solution: Redis INCR**

We use Redis to generate the sequence numbers (1, 2, 3). Redis is single-threaded and very fast.

```python
def send_message(conversation_id, sender_id, content, client_message_id):
    # 1. Get the next number from Redis
    seq = redis.incr(f"seq:{conversation_id}")

    # 2. Save to DB with that number
    message = db.execute(
        """
        INSERT INTO messages (conversation_id, sequence_number, ...)
        VALUES ($1, $2, ...)
    """,
        conversation_id,
        seq,
        ...,
    )

    return message
```



This is fast. The downside: If the database insert fails, we might have a gap in numbers (1, 2, 4). The client needs logic to handle gaps or request missing items.

### Problem 2: Read Receipts (Too Many Writes)

If a user scrolls through a chat, they might "read" 100 messages in a second. We do not want to update the database 100 times.

**Solution: Debouncing**
Wait a few seconds before sending the update.

```javascript
// Client-side code
let pendingReadReceipt = null;
let timer = null;

function onMessageViewed(sequenceNumber) {
  pendingReadReceipt = sequenceNumber;
  clearTimeout(timer);
  // Wait 2 seconds before sending to server
  timer = setTimeout(() => {
    sendReadReceipt(pendingReadReceipt);
  }, 2000);
}
```



The server only updates if the new number is higher than the old number.

### Problem 3: Multi-Device Sync

The user has a phone and a laptop. Both need the message.

**Solution: Fan-out**
When sending a message to User B:

- Look up User B's devices in the `devices` table.
- Add the message to the Inbox of **every** device.
- Each device must reply "I got it" independently.
- If the user reads a message on the phone, the phone updates `read_receipts`. When the laptop syncs later, it sees the new "last read" number and updates its UI.

### Trade-offs

**Consistency vs. Availability:**
We choose **Consistency** for a single conversation. It is confusing if messages appear out of order. We accept a small delay to ensure order.

**Latency vs. Durability:**
We choose **Durability**. We must write the message to the hard drive (PostgreSQL) *before* we tell the sender "Sent." This adds milliseconds of latency, but ensures we don't lose data if the server crashes.

## Final Review Checklist

Before finishing, check that you covered these points:

**The Basics**

- [ ] Did you confirm it is 1-to-1 only?
- [ ] Did you list the 4-5 main features?
- [ ] Did you do the math for scale?
**Data & API**

- [ ] Did you explain the database tables?
- [ ] Did you explain why you use sequence numbers (not just time)?
- [ ] Did you choose WebSockets?
**Architecture**

- [ ] Did you draw the diagram?
- [ ] Did you explain Pub/Sub for routing?
- [ ] Did you explain how offline messages work?
**Deep Dives**

- [ ] Did you solve the message ordering problem?
- [ ] Did you solve the "too many read receipts" problem?
- [ ] Did you mention multi-device support?

## Quick Summary Table

| Feature | Solution | Why? |
| --- | --- | --- |
| **Connection** | WebSocket | Real-time, two-way talking. |
| **Routing** | Redis Pub/Sub | Easy to scale, handles server crashes. |
| **Storage** | PostgreSQL (Sharded) | Reliable, safe, good for structured data. |
| **Ordering** | Redis INCR | Fast atomic counters. |
| **Offline** | Inbox + In-flight queue | Ensures messages wait for the user. |
| **Read Status** | High-water mark | Efficient (just store the last number read). |
| **Presence** | Redis Heartbeat | Fast way to check who is online. |

This design is simpler than WhatsApp because there are no groups. However, you must focus deeply on **ordering** and **delivery guarantees**. That is where the difficulty lies.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100098*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/sd-q4-1to1-chat-system)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
