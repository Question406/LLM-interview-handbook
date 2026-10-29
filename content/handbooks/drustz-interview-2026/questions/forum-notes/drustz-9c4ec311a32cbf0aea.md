---
id: drustz-9c4ec311a32cbf0aea
section: forum-notes
order: 221
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 5: Handling Growth & Problems'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 5: Handling Growth & Problems'
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
## Phase 5: Handling Growth & Problems

### Meeting Performance Goals

**1. Fast Matchmaking**

- Keep different queues separate (don't mix 3-minute blitz with 3-day daily chess).
- Start looking for a close rating match (+/- 50 points). If they wait, expand the search (+/- 100 points).
- Use fast in-memory structures (like Redis sets) to find players.
**2. Fast Moves**

- Keep the active game state in Redis.
- Use "Sticky Sessions" or consistent hashing so requests for Game #123 always go to the same server.
- Send data via WebSocket directly; don't make the client ask for updates.
**3. Correctness**

- Use `version` numbers on the game state.
- If two moves arrive at the same time, the database checks the version. The second one will fail, and the client must refresh.

### Slow Spots and Fixes

**Problem: Hot Queues**

- *Issue:* Everyone plays "Blitz 5+0". That queue is huge.
- *Fix:* Split the queue by region (US, EU, Asia) or rating buckets (Beginner, Intermediate, Pro).
**Problem: Redis Memory Full**

- *Issue:* 80,000 active games take up space.
- *Fix:* Only keep active games in Redis. Once a game ends, move it to the SQL database and clear it from Redis.
**Problem: Duplicate Moves**

- *Issue:* Bad internet makes a phone send the same move twice.
- *Fix:* Use an `idempotency_key`. If the server sees the same key twice, it ignores the second one but returns "Success" so the phone stops retrying.

### Choice: Good Match vs. Fast Match

| Approach | Pros | Cons |
| --- | --- | --- |
| **Strict Rating** | Very fair games. | Long wait times. |
| **Loose Rating** | Instant games. | Skill gap is too big. |
| **Dynamic (Best)** | Start strict, then get looser. | Balances both. |

*Recommendation:* Use the Dynamic approach.

### Choice: Storing Game State

| Approach | Pros | Cons |
| --- | --- | --- |
| **Database Only** | Very safe. | Too slow for real-time. |
| **Memory Only** | Very fast. | If server crashes, game is lost. |
| **Hybrid (Best)** | Fast and safe. | More complex to build. |

*Recommendation:* Hybrid. Use Redis for the live game, save moves to Postgres for history.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
