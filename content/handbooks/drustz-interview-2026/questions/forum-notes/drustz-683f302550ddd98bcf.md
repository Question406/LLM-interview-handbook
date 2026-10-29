---
id: drustz-683f302550ddd98bcf
section: forum-notes
order: 217
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 1: What We Need to Build'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Phase 1: What We Need to Build'
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

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
