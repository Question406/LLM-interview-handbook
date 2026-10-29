---
id: drustz-60d535a3f7aa6ed68b
section: forum-notes
order: 220
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 4: System Architecture'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 4: System Architecture'
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
## Phase 4: System Architecture

### What Each Part Does

**Matchmaking Service**

- Organizes waiting lists based on game type (Time limit + Rated/Casual).
- Finds players with similar ratings.
- If a player waits too long, the system looks for a wider range of ratings.
- Creates the game and removes players from the queue.
**Game Service**

- The "Boss" of the game logic.
- Checks if moves are legal using a chess engine library.
- Calculates time used based on **server time**.
- Schedules timeouts (if a player does nothing, they lose).
- Saves the move to the database.
**WebSocket Gateway**

- Keeps the connection open with the player.
- Sends moves and clock updates instantly.
- Helps players reconnect if their internet flickers.

### How the Timer Works (Chess Clock)

We **do not** write to the database every second (tick-tock). That generates too much traffic. We use an event-based method.

```text
When a move happens:
Time Used = Current Server Time - Time When Turn Started
Time Left = Old Time Left - Time Used

If Time Left <= 0 -> Player loses (Timeout)
Else -> Add Increment Time (e.g., +2 seconds)

Switch Active Player
Save New "Turn Start Time"
```



**Why is this better?**

- We calculate the exact time only when necessary (on a move or check).
- No "ticking" load on the database.
- The server is the source of truth. It doesn't matter what the client says.

```typescript
function applyMoveAndClock(
  state: ClockState,
  nowMs: number,
  incrementMs: number,
): ClockState {
  const elapsed = nowMs - state.turn_started_server_ms;

  if (state.active_side === "white") {
    state.white_remaining_ms -= elapsed;
    if (state.white_remaining_ms <= 0) throw new Error("white_timeout");
    state.white_remaining_ms += incrementMs;
    state.active_side = "black";
  } else {
    state.black_remaining_ms -= elapsed;
    if (state.black_remaining_ms <= 0) throw new Error("black_timeout");
    state.black_remaining_ms += incrementMs;
    state.active_side = "white";
  }

  state.turn_started_server_ms = nowMs;
  state.version += 1;
  return state;
}
```



**Handling Timeouts:**

- After a move, the server sets a background timer for the *maximum* time the next player has.
- If that background timer fires, we check the database. If the player hasn't moved yet, they lose.

### Handling Disconnects

- **Redis** (Fast Memory): Stores the current board, move number, and clock state.
- **PostgreSQL** (Storage): Stores the full history of moves.
- When a player reconnects, they ask `GET /game`. We send them the latest snapshot from Redis so they can resume instantly.
- The clock keeps running even if you disconnect.

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
