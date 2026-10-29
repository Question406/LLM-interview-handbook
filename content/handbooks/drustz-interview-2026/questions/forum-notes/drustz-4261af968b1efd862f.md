---
id: drustz-4261af968b1efd862f
section: forum-notes
order: 328
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: First Solution - Using Interfaces'
quick: >-
  作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: First Solution - Using
  Interfaces
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
## Part 2: First Solution - Using Interfaces

### Refactoring Goals

Create an interface named `IBotService`. It needs two methods:

- **`shouldActivate`**: Check if the bot needs to run.
- **`execute`**: Run the bot logic and return a list of messages.
You need to:

- Make a separate class for each bot.
- Register these bots in a chat room class.
- Loop through the bots when a message comes in.

### Solution: Using Interfaces

```python
from abc import ABC, abstractmethod
from typing import List


class IBotService(ABC):
    """Interface for chat bots"""

    @abstractmethod
    def should_activate(self, name: str, msg: str) -> bool:
        """Check if this bot should respond to the message"""
        pass

    @abstractmethod
    def execute(self, name: str, msg: str) -> List[str]:
        """Execute bot logic and return response messages"""
        pass


class ChatRoom:
    def __init__(self):
        self.bots: List[IBotService] = []
        self.messages: List[str] = []

    def register_bot(self, bot: IBotService):
        """Register a bot with the chat room"""
        self.bots.append(bot)

    def send_message(self, name: str, msg: str):
        """Process a message through all registered bots"""
        # Add the user's message
        self.messages.append(f"{name}: {msg}")

        # Check each bot
        for bot in self.bots:
            if bot.should_activate(name, msg):
                bot_responses = bot.execute(name, msg)
                self.messages.extend(bot_responses)


class MeetBot(IBotService):
    def __init__(self, away_bot=None):
        self.away_bot = away_bot  # Pass AwayBot so we can update status

    def should_activate(self, name: str, msg: str) -> bool:
        return msg.startswith("/meet ")

    def execute(self, name: str, msg: str) -> List[str]:
        # Parse the command
        parts = msg.split(" ", 1)
        if len(parts) < 2:
            return []

        other_user = parts[1]

        # Generate meeting link
        response = f"MeetBot: Google Meet with @{name}, and {other_user} starting at https://meet.google.com/abc-def-123"

        # Update away status through AwayBot
        if self.away_bot:
            self.away_bot.set_away(name, f"@{name} may be in a meeting right now")
            self.away_bot.set_away(
                other_user, f"@{other_user} may be in a meeting right now"
            )

        return [response]


class TacoBot(IBotService):
    def __init__(self):
        self.taco_counts: dict[str, int] = {}

    def should_activate(self, name: str, msg: str) -> bool:
        return msg.startswith("/givetaco ")

    def execute(self, name: str, msg: str) -> List[str]:
        # Parse: /givetaco 🌮🌮 @username
        parts = msg.split(" ")
        if len(parts) < 3:
            return []

        taco_string = parts[1]
        recipient = parts[2]

        # Count tacos and fix username format
        num_tacos = len(taco_string)
        username = recipient.lstrip("@")

        # Update count
        if username not in self.taco_counts:
            self.taco_counts[username] = 0
        self.taco_counts[username] += num_tacos

        # Format response
        response = f"TacoBot: @{name} gave @{recipient} {num_tacos} 🌮's. {recipient} now have {self.taco_counts[username]} 🌮s."

        return [response]


class AwayBot(IBotService):
    def __init__(self):
        self.away_statuses: dict[str, str] = {}

    def should_activate(self, name: str, msg: str) -> bool:
        # Check if setting away status
        if msg.startswith("/away "):
            return True

        # Check if message mentions someone who is away
        for away_user in self.away_statuses:
            if away_user in msg:
                return True

        return False

    def execute(self, name: str, msg: str) -> List[str]:
        responses = []

        # Handle /away command
        if msg.startswith("/away "):
            away_message = msg[6:]  # Everything after "/away "
            self.set_away(name, away_message)
            return []  # /away command doesn't produce a message

        # Check for mentions of away users
        for away_user, away_msg in self.away_statuses.items():
            if away_user in msg:
                responses.append(f"AwayBot: {away_user} is away: {away_msg}")

        return responses

    def set_away(self, username: str, message: str):
        """Public method for other bots to set away status"""
        self.away_statuses[username] = message


# Usage
chat_room = ChatRoom()

# Create bots with dependencies
away_bot = AwayBot()
meet_bot = MeetBot(away_bot=away_bot)
taco_bot = TacoBot()

# Register bots
chat_room.register_bot(away_bot)
chat_room.register_bot(meet_bot)
chat_room.register_bot(taco_bot)

# Send messages
chat_room.send_message("Alice", "Hello")
chat_room.send_message("Cindy", "/givetaco 🌮🌮 @justin")
# ... etc
```



### Why This Design Works

- **Dependency Injection**: `MeetBot` is given access to `AwayBot` so it can change status.
- **Encapsulation**: Each bot keeps its own data private (like taco counts).
- **Single Responsibility**: Each class does only one thing.
- **Open/Closed Principle**: You can add new bots without touching the old ones.
- **Testability**: You can test one bot without running the others.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
