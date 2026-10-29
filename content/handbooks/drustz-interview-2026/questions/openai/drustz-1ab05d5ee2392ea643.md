---
id: drustz-1ab05d5ee2392ea643
section: openai
order: 11
level: A
title: Design Chess Game
quick: locally-saved-topic-editorial · Design Chess Game
companies:
  - openai
tags:
  - DrustZ
  - locally-saved-topic-editorial
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/company/openai/design-chess-game
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Design Chess.com (Online Chess Game)

### Design Chess.com (Online Chess Game)

Design an online chess platform like Chess.com. Users need to find opponents quickly, play in real time, and the chess clock must be accurate (time limits with optional extra time per move).

This problem tests if you can design **matchmaking**, **secure move handling**, and **server-side timing** while keeping everything fast (**low latency**).

## Phase 1: What We Need to Build

### Basic Features

- **Join Queue:** Users select settings (time limit, rated vs. casual) to find a game.
- **Start Game:** The system pairs two players and begins the match.
- **Play Moves:** Users make moves and see the opponent's moves instantly.
- **Chess Clock:** The system tracks time accurately. Players lose if time runs out.
- **Game Actions:** Users can resign, offer a draw, or reconnect if the internet drops.
Assume this is standard 1-vs-1 chess. No tournaments or bots unless asked.

### Performance Goals

| Goal | Target | Why? |
| --- | --- | --- |
| **Match Speed (P95)** | < 5 seconds | Players hate waiting in queues. |
| **Move Speed (P95)** | < 150ms | The game must feel real-time. |
| **Clock Accuracy** | < 100ms | Timers must be exact to be fair. |
| **Availability** | 99.95% | Games should not crash. |
| **Safety** | No lost moves | Players must trust the game history. |

**Crucial Rule:** The server is the boss of the clock. The timer on the user's screen is just a display.

### Scale Numbers

**Assumptions:**

- 2 million players per day.
- Peak traffic is 8% of players = 160,000 people online at once.
- 2 players per game = 80,000 games happening at once.
- Average speed: 1 move every 8 seconds per game.
**Data Speed:**

- **Move Writes:** 80K games / 8 seconds = 10,000 moves per second.
- **Sending Moves:** We send updates to both players, so ~20,000 events per second.
- **Bandwidth:** This is about 6 MB/sec. This is low.
**Matchmaking Queue:**

- If 10% of players are waiting: 16,000 people in the queue.
- The system needs to insert and remove players very fast.
**Interview Tip:** Mention that the *volume* of data is easy. The hard part is **latency** (speed) and **correctness** (rules/timing).

## Phase 2: How We Store Data

### Database Tables

```text
Player
├── id: UUID
├── username: string
├── rating_blitz: int
├── rating_rapid: int
└── created_at: timestamp

QueueEntry
├── id: UUID
├── player_id: UUID (FK)
├── mode: enum (rated, casual)
├── time_control: string (e.g., "5+0", "10+5")
├── rating: int
├── region: string
├── joined_at: timestamp
└── status: enum (waiting, matched, cancelled, expired)

Game
├── id: UUID
├── white_player_id: UUID (FK)
├── black_player_id: UUID (FK)
├── mode: enum (rated, casual)
├── time_control_base_ms: bigint
├── increment_ms: int
├── status: enum (active, white_won, black_won, draw, aborted)
├── result_reason: enum (checkmate, resignation, timeout, draw, disconnect_forfeit)
├── current_fen: string
├── move_count: int
├── turn: enum (white, black)
├── started_at: timestamp
└── ended_at: timestamp

MoveEvent
├── id: UUID
├── game_id: UUID (FK)
├── move_number: int
├── player_id: UUID
├── uci: string (e2e4)
├── san: string (optional)
├── fen_after: string
├── remaining_white_ms: bigint
├── remaining_black_ms: bigint
├── server_received_at: timestamp
└── is_legal: boolean

ClockState
├── game_id: UUID (PK/FK)
├── white_remaining_ms: bigint
├── black_remaining_ms: bigint
├── active_side: enum (white, black)
├── turn_started_server_ms: bigint (Official server time)
└── version: bigint
```



### How Tables Connect

```text
Player 1:N QueueEntry
Player 1:N Game (as white/black)
Game 1:N MoveEvent
Game 1:1 ClockState
```



We store every single move (`MoveEvent`) for history. We also store the current board state (`Game.current_fen` and `ClockState`) so we can read it quickly.

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

## Common Mistakes

- **Trusting the Client:** Never assume the client clock is right. Users can hack their app to stop the timer.
- **Ticking Clock:** Writing to the DB every second ($1s, 2s, 3s...$) kills performance. Calculate time by subtraction instead.
- **One Big Queue:** Mixing all players in one list makes matchmaking very slow and hard to filter.

## Interview Checklist

### Requirements

- [ ] Checked difference between rated and casual.
- [ ] Defined speed targets (latency) and clock accuracy.
- [ ] Explained what happens when a player disconnects.

### Design

- [ ] Explained how the queue expands rating range over time.
- [ ] Designed a secure way to process moves.
- [ ] Explained the "Subtraction" method for the clock (not ticking).
- [ ] Covered how to resume a game after a crash.

### Scaling

- [ ] Discussed splitting queues to handle high traffic.
- [ ] Mentioned `idempotency` to handle retries.
- [ ] Explained why we use both Redis and SQL.

## Final Summary

| Aspect | Decision | Why? |
| --- | --- | --- |
| **Matchmaking** | Separate queues + Expanding range | Balances fairness with speed. |
| **Game Logic** | Server checks everything | Prevents cheating and bugs. |
| **Clock** | Event-based math | Accurate without overloading the DB. |
| **Active Storage** | Redis | Super fast for live games. |
| **History Storage** | PostgreSQL | Permanent record for replay and analysis. |
| **Transport** | WebSocket | Immediate updates (<150ms). |

**Main Takeaway:** This system isn't just about handling lots of users; it's about **fairness**. If the matching is bad or the clock is wrong, players will leave. The server must always be the single source of truth.

*原帖: [来源链接](https://www.1point3acres.com/interview/thread/7100178*)

---

### 来源与内容类型

- Content kind: `locally-saved-topic-editorial`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/design-chess-game)
- [相关来源](https://www.1point3acres.com/bbs/thread-1172810-1-1.html)
- [相关来源](https://www.1point3acres.com/bbs/thread-1181839-1-1.html)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。
