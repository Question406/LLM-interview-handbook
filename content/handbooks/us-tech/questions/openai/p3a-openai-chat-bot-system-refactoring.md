---
id: p3a-openai-chat-bot-system-refactoring
section: openai
order: 612
level: A
title: "OpenAI：聊天机器人重构：从全局状态到事件总线"
quick: "先用现有输入输出写行为测试固定行为，再拆出命令解析、按命令注册的 bot handler 和实例内的会话状态；改成事件总线时要定义订阅顺序和取消方式，并用 is_bot 标记防止 bot 的回复再次触发 bot。"
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · chat-bot-system-refactoring"
    url: https://www.1point3acres.com/interview/problems/company/openai/chat-bot-system-refactoring
    type: secondary
---

## 题目

给一个支持 slash 命令的聊天服务做重构。服务里有 AwayBot、MeetBot、TacoBot 三个机器人，原代码把它们的逻辑和全局状态混在一起。要求在不改变行为的前提下理清结构，后续追问会要求改成事件驱动（事件总线）。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

重构的第一步是先用现有的输入输出写几条行为测试，把当前行为固定下来，之后每改一步都跑一遍，重构前后必须通过同一组用例。

然后按职责拆开：

- 命令解析：把消息文本拆成命令名和参数；
- 机器人接口：每个 bot 是一个「接收消息和参数、返回回复文本」的 handler，按命令名注册，增加新 bot 不用改分发逻辑；
- 会话状态：消息日志等状态放进 `Chat` 实例，不用模块级全局变量。

改成事件总线时，要把这几件事说清楚：有哪些事件类型、订阅什么时候建立和取消、同一事件的多个 handler 按什么顺序执行、handler 抛异常怎么办。最容易出的问题是 bot 的回复本身也是一条消息，会再次触发 bot，形成无限递归。这份练习用消息上的 `is_bot` 标记切断这条路径，而不是依赖回复文本里不含 slash。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `EventBus.subscribe(event, handler)`：返回一个取消订阅的函数。
- `EventBus.emit(event, payload)`：按订阅顺序同步调用 handler，遍历的是调用 `emit` 那一刻的订阅快照；handler 的异常直接向上传播，不做异步。
- `Chat.send(channel, user, text, is_bot=False)`：把消息作为 `"message"` 事件发布。`Chat.register(name, handler)` 注册 slash 命令，命令名不以 `/` 开头抛 `ValueError`。
- `default_chat()`：注册 `/away`（返回离开提示）、`/meet`（返回由 channel 决定的会议链接）、`/taco`（返回感谢）。
- bot 的回复标记 `is_bot=True`，不会再触发任何命令。日志 `log` 是全部消息，`history(channel)` 按 channel 过滤。
- 最多 1000 条消息。

### 输入输出示例

```text
chat = default_chat()
chat.send("a", "u", "/away lunch")   -> log: ["/away lunch", "away: lunch"]
chat.send("b", "u", "hi")            -> 只多一条 "hi"，没有 bot 回复
chat.send("a", "bot", "/taco u", is_bot=True)   -> 只记录这一条，不触发 /taco
chat.send("b", "u", "/meet")         -> bot 回复 "https://meet.example/b"
```

### 解题思路与正确性

`Chat` 构造时先订阅记录日志的 handler，再订阅分发命令的 handler。事件总线按订阅顺序调用，所以用户消息总是先进日志，bot 的回复在命令 handler 里再次 `send`，排在它后面。

`Chat` 只管消息的生命周期，具体 bot 都是注册进来的 handler，增加命令不需要改分发代码。递归由 `is_bot` 切断：bot 回复带着这个标记，命令分发看到它就直接返回。`emit` 遍历订阅列表的副本，所以 handler 在本轮里取消订阅自己或别人，不会让当前这轮跳过或重复调用。

### 完整参考实现（Python 3）

```python
class EventBus:
    """同步事件总线：emit 按订阅顺序调用 handler，异常直接向上传播。"""

    def __init__(self):
        self.handlers = {}  # event -> handler 列表

    def subscribe(self, event, handler):
        """订阅事件，返回一个取消订阅的函数（重复调用无副作用）。"""
        self.handlers.setdefault(event, []).append(handler)

        def unsubscribe():
            handlers = self.handlers.get(event, [])
            if handler in handlers:
                handlers.remove(handler)

        return unsubscribe

    def emit(self, event, payload):
        # 遍历订阅列表的快照：handler 在本轮里取消订阅，不影响本轮的遍历
        for handler in list(self.handlers.get(event, [])):
            handler(payload)


class Chat:
    """聊天服务只管消息的发布和记录；各个 bot 以 slash 命令的形式注册进来。"""

    def __init__(self, bus):
        self.bus = bus
        self.log = []
        self.commands = {}  # "/name" -> handler(message, argument) -> 回复文本
        # 先记录、再分发给 bot，所以日志里用户消息总在 bot 回复之前
        bus.subscribe("message", self._record)
        bus.subscribe("message", self._dispatch_command)

    def register(self, name, handler):
        if not name.startswith("/"):
            raise ValueError(f"command must start with '/': {name!r}")
        self.commands[name] = handler

    def send(self, channel, user, text, is_bot=False):
        message = {"channel": channel, "user": user, "text": text, "is_bot": is_bot}
        self.bus.emit("message", message)

    def history(self, channel):
        """某个 channel 的消息，按发送顺序。"""
        return [message for message in self.log if message["channel"] == channel]

    def _record(self, message):
        self.log.append(dict(message))

    def _dispatch_command(self, message):
        # bot 的消息不再触发命令，靠 is_bot 标记而不是文本内容切断递归
        if message["is_bot"]:
            return
        parts = message["text"].split(maxsplit=1)
        command = parts[0] if parts else ""
        if command not in self.commands:
            return
        argument = parts[1] if len(parts) > 1 else ""
        reply = self.commands[command](message, argument)
        self.send(message["channel"], "bot", reply, is_bot=True)


def default_chat():
    """注册 AwayBot、MeetBot、TacoBot 三个命令的聊天服务。"""
    chat = Chat(EventBus())
    chat.register("/away", lambda message, argument: "away: " + argument)
    chat.register("/meet", lambda message, argument: "https://meet.example/" + message["channel"])
    chat.register("/taco", lambda message, argument: "thanks " + argument)
    return chat
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 命令触发 bot 回复，日志里用户消息在前
chat = default_chat()
chat.send("a", "u", "/away lunch")
assert [message["text"] for message in chat.log] == ["/away lunch", "away: lunch"]

# 普通消息不触发 bot
chat.send("b", "u", "hi")
assert len(chat.log) == 3

# bot 发出的消息即使以 slash 开头也不会再触发命令
chat.send("a", "bot", "/taco u", True)
assert len(chat.log) == 4

# /meet 的链接由 channel 决定；history 按 channel 过滤
chat.send("b", "u", "/meet")
assert chat.log[-1]["text"] == "https://meet.example/b"
assert [message["text"] for message in chat.history("b")] == ["hi", "/meet", "https://meet.example/b"]

# 命令名必须以 / 开头
expect_value_error(chat.register, "away", lambda message, argument: "")

# 取消订阅后不再收到事件
bus = EventBus()
received = []
unsubscribe = bus.subscribe("x", received.append)
bus.emit("x", 1)
unsubscribe()
bus.emit("x", 2)
assert received == [1]

# handler 在 emit 过程中取消订阅，本轮仍按快照调用完
bus = EventBus()
calls = []
unsubscribe_second = None

def first(payload):
    calls.append("first")
    unsubscribe_second()

def second(payload):
    calls.append("second")

bus.subscribe("x", first)
unsubscribe_second = bus.subscribe("x", second)
bus.emit("x", None)
bus.emit("x", None)
assert calls == ["first", "second", "first"]
```

### 复杂度与追问

设订阅者数为 H、消息数为 M。每次 `emit` 是 O(H)（复制订阅列表加逐个调用）；日志占 O(M)；`history` 是 O(M)，频繁查询时可以改成按 channel 分桶存。

这个事件总线是同步、进程内的，没有持久投递和重试。如果迁移成异步或跨进程，要额外解决：给每个事件分配 id，让 handler 能按 id 做幂等处理；约定是否保证同一 channel 内的顺序；一个 handler 出错时不能拖垮其他 handler，失败的事件进重试队列或死信队列。
