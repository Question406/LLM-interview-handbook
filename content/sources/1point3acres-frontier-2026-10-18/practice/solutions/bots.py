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


def test():
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


if __name__ == "__main__":
    test()
