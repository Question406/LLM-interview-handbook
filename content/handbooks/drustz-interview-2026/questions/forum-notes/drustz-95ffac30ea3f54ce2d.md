---
id: drustz-95ffac30ea3f54ce2d
section: forum-notes
order: 327
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Looking at the Old Code'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 1: Looking at the Old Code'
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
## Part 1: Looking at the Old Code

### The Legacy Code

Here is the code you need to fix:

```python
aways: dict[str, str] = {}
tacos: dict[str, int] = {}
messages = []


def sendMessage(name: str, msg: str) -> None:
    messages.append(name + ": " + msg)

    # AwayBot logic
    for away, away_msg in aways.items():
        if away in msg:
            messages.append(f"AwayBot: {away} is away: {away_msg}")

    # MeetBot logic
    if msg[1:5] == "meet":
        messages.append(
            "MeetBot: Google Meet with @"
            + name
            + ", and "
            + msg[6:]
            + " starting at https://meet.google.com/abc-def-123"
        )
        aways[name] = "@" + name + " may be in a meeting right now"
        aways[msg[7:]] = "@" + msg[7:] + " may be in a meeting right now"

    # TacoBot logic
    if msg[1:9] == "givetaco":
        num_tacos = len(msg.split(" ")[1])
        who = msg.split(" ")[2]
        if who[1:] not in tacos:
            tacos[who[1:]] = 0
        tacos[who[1:]] += num_tacos
        messages.append(
            "TacoBot: @"
            + name
            + " gave @"
            + who
            + " "
            + str(num_tacos)
            + " 🌮's. "
            + who
            + f" now have {tacos[who[1:]]} 🌮s."
        )

    # Away status logic
    if msg[1:5] == "away":
        aways[name] = msg[6:]
```



### Required Output

Your new code must produce the exact same output for these inputs:

```python
sendMessage(name="Alice", msg="Hello")
sendMessage(name="Bob", msg="Hi")
sendMessage(name="Alice", msg="Nice job on your presentations")
sendMessage(name="Cindy", msg="/givetaco 🌮🌮 @justin")
sendMessage(name="Alice", msg="Bob let's meet")
sendMessage(name="Bob", msg="/meet Alice")
sendMessage(name="David", msg="/away out for lunch")
sendMessage(name="Emily", msg="Anyone around?")
sendMessage(name="Frank", msg="/meet David")

assert messages == [
    "Alice: Hello",
    "Bob: Hi",
    "Alice: Nice job on your presentations",
    "Cindy: /givetaco 🌮🌮 @justin",
    "TacoBot: @Cindy gave @@justin 2 🌮's. @justin now have 2 🌮s.",
    "Alice: Bob let's meet",
    "Bob: /meet Alice",
    "MeetBot: Google Meet with @Bob, and Alice starting at https://meet.google.com/abc-def-123",
    "David: /away out for lunch",
    "Emily: Anyone around?",
    "Frank: /meet David",
    "AwayBot: David is away: out for lunch",
    "MeetBot: Google Meet with @Frank, and David starting at https://meet.google.com/abc-def-123",
]
```



### What the Bots Do

- **AwayBot**:

Watches for mentions of users who are away.
- Replies with that user's away message.
- Users set their status with `/away <message>`.
- **MeetBot**:

Starts when it sees `/meet <username>`.
- Makes a meeting link.
- Sets both users' status to "may be in a meeting right now".
- **TacoBot**:

Starts when it sees `/givetaco <tacos> <@username>`.
- Counts the taco emojis.
- Keeps a total count of tacos for each user.
- Announces the gift and the new total.

### Why the Old Code is Bad

Before fixing it, let's list the problems:

- **Tight coupling**: All logic is stuck in one function.
- **Global state**: `aways` and `tacos` are global variables.
- **Hard to extend**: Adding a new bot means changing the main function.
- **Messy logic**: Parsing strings and business rules are mixed.
- **Hard to test**: You cannot test just one bot by itself.
- **No validation**: It assumes every command is typed perfectly.
- **Bad readability**: String slicing makes it hard to read.
- **Dependencies**: It is hard for bots to talk to each other cleanly.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
