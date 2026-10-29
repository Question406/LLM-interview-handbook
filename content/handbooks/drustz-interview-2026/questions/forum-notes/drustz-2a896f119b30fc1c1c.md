---
id: drustz-2a896f119b30fc1c1c
section: forum-notes
order: 20
level: A
title: >-
  Anthropic 面试题库 · 一亩三分地会员版（完整） · Phase 5: Handling Scale & Challenges (~15-20
  minutes)
quick: >-
  作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Phase 5: Handling Scale & Challenges
  (~15-20 minutes)
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

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
