---
id: drustz-e10fcd27e53509e65c
section: forum-notes
order: 329
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 3: Advanced Solution - Using Events'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 3: Advanced Solution - Using Events'
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
## Part 3: Advanced Solution - Using Events

The interviewer might say that passing bots into other bots (Dependency Injection) gets messy if you have many bots. They might ask for an **Event-Driven Architecture**.

### New Requirements

Refactor the code so:

- Bots publish "Events".
- Other bots listen (subscribe) to these events.
- Bots do not need to know about each other directly.
- A central "Event Bus" handles the communication.

### Code: Event-Driven Approach

```python
from abc import ABC, abstractmethod
from typing import List, Callable, Dict
from dataclasses import dataclass


@dataclass
class Event:
    """Base class for events"""

    event_type: str
    data: dict


class EventBus:
    """Central hub for bot communication"""

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Event], None]):
        """Listen for a specific event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event: Event):
        """Send an event to all listeners"""
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                handler(event)


class IBotService(ABC):
    """Interface for chat bots"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.setup_subscriptions()

    def setup_subscriptions(self):
        """Override to subscribe to events"""
        pass

    @abstractmethod
    def should_activate(self, name: str, msg: str) -> bool:
        pass

    @abstractmethod
    def execute(self, name: str, msg: str) -> List[str]:
        pass


class AwayBot(IBotService):
    def __init__(self, event_bus: EventBus):
        self.away_statuses: dict[str, str] = {}
        super().__init__(event_bus)

    def setup_subscriptions(self):
        # Listen for meeting events to set away status
        self.event_bus.subscribe("user_meeting_started", self.handle_meeting_started)

    def handle_meeting_started(self, event: Event):
        """Handle when a user starts a meeting"""
        username = event.data["username"]
        self.away_statuses[username] = f"@{username} may be in a meeting right now"

    def should_activate(self, name: str, msg: str) -> bool:
        if msg.startswith("/away "):
            return True

        for away_user in self.away_statuses:
            if away_user in msg:
                return True

        return False

    def execute(self, name: str, msg: str) -> List[str]:
        responses = []

        if msg.startswith("/away "):
            away_message = msg[6:]
            self.away_statuses[name] = away_message

            # Publish event
            self.event_bus.publish(
                Event(
                    event_type="user_away_status_changed",
                    data={"username": name, "message": away_message},
                )
            )
            return []

        for away_user, away_msg in self.away_statuses.items():
            if away_user in msg:
                responses.append(f"AwayBot: {away_user} is away: {away_msg}")

        return responses


class MeetBot(IBotService):
    def setup_subscriptions(self):
        # MeetBot doesn't need to listen to events here
        pass

    def should_activate(self, name: str, msg: str) -> bool:
        return msg.startswith("/meet ")

    def execute(self, name: str, msg: str) -> List[str]:
        parts = msg.split(" ", 1)
        if len(parts) < 2:
            return []

        other_user = parts[1]

        # Publish events for both participants
        self.event_bus.publish(
            Event(event_type="user_meeting_started", data={"username": name})
        )
        self.event_bus.publish(
            Event(event_type="user_meeting_started", data={"username": other_user})
        )

        response = f"MeetBot: Google Meet with @{name}, and {other_user} starting at https://meet.google.com/abc-def-123"
        return [response]


class TacoBot(IBotService):
    def __init__(self, event_bus: EventBus):
        self.taco_counts: dict[str, int] = {}
        super().__init__(event_bus)

    def setup_subscriptions(self):
        pass  # TacoBot doesn't listen to events

    def should_activate(self, name: str, msg: str) -> bool:
        return msg.startswith("/givetaco ")

    def execute(self, name: str, msg: str) -> List[str]:
        parts = msg.split(" ")
        if len(parts) < 3:
            return []

        taco_string = parts[1]
        recipient = parts[2]
        num_tacos = len(taco_string)
        username = recipient.lstrip("@")

        if username not in self.taco_counts:
            self.taco_counts[username] = 0
        self.taco_counts[username] += num_tacos

        # Publish event
        self.event_bus.publish(
            Event(
                event_type="tacos_given",
                data={
                    "giver": name,
                    "recipient": username,
                    "count": num_tacos,
                    "total": self.taco_counts[username],
                },
            )
        )

        response = f"TacoBot: @{name} gave @{recipient} {num_tacos} 🌮's. {recipient} now have {self.taco_counts[username]} 🌮s."
        return [response]


class ChatRoom:
    def __init__(self):
        self.event_bus = EventBus()
        self.bots: List[IBotService] = []
        self.messages: List[str] = []

    def register_bot(self, bot: IBotService):
        self.bots.append(bot)

    def send_message(self, name: str, msg: str):
        self.messages.append(f"{name}: {msg}")

        for bot in self.bots:
            if bot.should_activate(name, msg):
                bot_responses = bot.execute(name, msg)
                self.messages.extend(bot_responses)


# Usage
chat_room = ChatRoom()

# Create bots with shared event bus
away_bot = AwayBot(chat_room.event_bus)
meet_bot = MeetBot(chat_room.event_bus)
taco_bot = TacoBot(chat_room.event_bus)

# Register bots
chat_room.register_bot(away_bot)
chat_room.register_bot(meet_bot)
chat_room.register_bot(taco_bot)
```



### Why Use Events?

- **Loose Coupling**: Bots do not need to link to each other.
- **Scalability**: You can add many new bots that listen to the same events.
- **Flexibility**: An event can trigger actions in multiple different bots.
- **Testability**: You can fake the events to test how a bot reacts.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
