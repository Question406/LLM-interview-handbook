---
id: drustz-a819fdfa3cb532c4ed
section: forum-notes
order: 219
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 3: Communication Rules (API)'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 3: Communication Rules (API)'
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
## Phase 3: Communication Rules (API)

### Choosing How to Connect

| Action | Protocol | Reason |
| --- | --- | --- |
| **Joining Queue** | REST | Simple request and response. |
| **Playing Moves** | WebSocket | Needs to be super fast and two-way. |
| **Internal Servers** | gRPC | Strictly typed and fast for servers talking to servers. |

### HTTP Commands (REST)

```text
# Finding a Match
POST   /api/chess/queue                    Join the line
DELETE /api/chess/queue/{entry_id}         Leave the line
GET    /api/chess/queue/status             Check if matched

# Game Actions
GET    /api/chess/games/{game_id}          Get game board
POST   /api/chess/games/{game_id}/move     Make a move
POST   /api/chess/games/{game_id}/resign   Give up
POST   /api/chess/games/{game_id}/draw     Offer draw
POST   /api/chess/games/{game_id}/abort    Cancel (only at start)
GET    /api/chess/games/{game_id}/moves    Get list of past moves
```



**Request to make a move:**

```json
{
  "move_number": 17,
  "uci": "e2e4",
  "client_sent_at_ms": 1730000000000,
  "idempotency_key": "4f8d7a3f"
}
```



**Response (Success):**

```json
{
  "accepted": true,
  "game_id": "game-123",
  "move_number": 17,
  "fen_after": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
  "turn": "black",
  "remaining_white_ms": 178450,
  "remaining_black_ms": 180000,
  "game_status": "active"
}
```



### Real-Time Messages (WebSocket)

```text
WSS /ws/chess?token=<signed_jwt>
```



```text
{ "type": "game.matched", "game_id": "game-123", "color": "white", "opponent": { "id": "u2", "rating": 1830 } }
{ "type": "game.move", "game_id": "game-123", "move_number": 17, "uci": "e2e4", "fen_after": "...", "turn": "black" }
{ "type": "game.clock_sync", "game_id": "game-123", "white_remaining_ms": 178450, "black_remaining_ms": 180000, "server_now_ms": 1730000001234 }
{ "type": "game.ended", "game_id": "game-123", "result": "white_won", "reason": "timeout" }
```



Every move must have a `move_number`. If the server receives move #17 twice, it knows to ignore the second one.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
