---
id: drustz-d39d81f93ad7d7c1b3
section: forum-notes
order: 330
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 4: Testing the Code'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 4: Testing the Code'
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
## Part 4: Testing the Code

The interviewer may ask you to prove your code works by writing tests.

### Testing Individual Bots

```python
import unittest


class TestTacoBot(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.taco_bot = TacoBot(self.event_bus)

    def test_should_activate_on_givetaco_command(self):
        self.assertTrue(self.taco_bot.should_activate("Alice", "/givetaco 🌮🌮 @bob"))
        self.assertFalse(self.taco_bot.should_activate("Alice", "Hello"))

    def test_execute_gives_tacos(self):
        responses = self.taco_bot.execute("Alice", "/givetaco 🌮🌮🌮 @bob")

        self.assertEqual(len(responses), 1)
        self.assertIn("3 🌮's", responses[0])
        self.assertIn("now have 3 🌮s", responses[0])

    def test_accumulates_tacos(self):
        self.taco_bot.execute("Alice", "/givetaco 🌮🌮 @bob")
        responses = self.taco_bot.execute("Charlie", "/givetaco 🌮 @bob")

        self.assertIn("now have 3 🌮s", responses[0])


class TestMeetBot(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.meet_bot = MeetBot(self.event_bus)

        # Keep track of published events
        self.published_events = []
        self.event_bus.subscribe(
            "user_meeting_started", lambda e: self.published_events.append(e)
        )

    def test_creates_meeting_link(self):
        responses = self.meet_bot.execute("Alice", "/meet Bob")

        self.assertEqual(len(responses), 1)
        self.assertIn("Google Meet with @Alice, and Bob", responses[0])
        self.assertIn("https://meet.google.com", responses[0])

    def test_publishes_meeting_events(self):
        self.meet_bot.execute("Alice", "/meet Bob")

        self.assertEqual(len(self.published_events), 2)
        self.assertEqual(self.published_events[0].data["username"], "Alice")
        self.assertEqual(self.published_events[1].data["username"], "Bob")


class TestAwayBot(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.away_bot = AwayBot(self.event_bus)

    def test_set_away_status(self):
        responses = self.away_bot.execute("David", "/away out for lunch")

        # /away doesn't produce an output message
        self.assertEqual(len(responses), 0)
        self.assertIn("David", self.away_bot.away_statuses)

    def test_notify_when_away_user_mentioned(self):
        self.away_bot.execute("David", "/away out for lunch")
        responses = self.away_bot.execute("Alice", "Hey David, are you around?")

        self.assertEqual(len(responses), 1)
        self.assertIn("David is away", responses[0])

    def test_handles_meeting_started_event(self):
        event = Event(event_type="user_meeting_started", data={"username": "Alice"})
        self.away_bot.handle_meeting_started(event)

        self.assertIn("Alice", self.away_bot.away_statuses)
        self.assertIn("may be in a meeting", self.away_bot.away_statuses["Alice"])
```



### Testing the Whole System

```python
class TestChatRoomIntegration(unittest.TestCase):
    def setUp(self):
        self.chat_room = ChatRoom()

        away_bot = AwayBot(self.chat_room.event_bus)
        meet_bot = MeetBot(self.chat_room.event_bus)
        taco_bot = TacoBot(self.chat_room.event_bus)

        self.chat_room.register_bot(away_bot)
        self.chat_room.register_bot(meet_bot)
        self.chat_room.register_bot(taco_bot)

    def test_full_conversation_flow(self):
        self.chat_room.send_message("Alice", "Hello")
        self.chat_room.send_message("Bob", "/meet Alice")
        self.chat_room.send_message("Charlie", "Hey Bob")

        messages = self.chat_room.messages

        # Check user messages
        self.assertIn("Alice: Hello", messages)
        self.assertIn("Bob: /meet Alice", messages)

        # Check MeetBot response
        self.assertTrue(
            any("MeetBot" in msg and "Google Meet" in msg for msg in messages)
        )

        # Check AwayBot response (Bob is in a meeting)
        self.assertTrue(
            any("AwayBot" in msg and "Bob is away" in msg for msg in messages)
        )
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
