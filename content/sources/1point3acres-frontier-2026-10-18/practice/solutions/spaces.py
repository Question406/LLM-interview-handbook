class Room:
    def __init__(self):
        self.joined_at = {}     # 在线用户 -> 加入时刻
        self.closed_total = 0   # 已离开会话的人秒数之和


class Spaces:
    """按时间顺序处理 create / join / leave 事件，统计每个房间的用户在线人秒数。"""

    def __init__(self):
        self.rooms = {}
        self.last_time = float("-inf")

    def _advance_clock(self, t):
        if t < self.last_time:
            raise ValueError(f"time went backwards: {t} < {self.last_time}")
        self.last_time = t

    def event(self, op, space, user, t):
        self._advance_clock(t)
        if op == "create":
            self.rooms.setdefault(space, Room())  # 重复 create 不重置房间
            return
        if space not in self.rooms:
            raise ValueError(f"unknown space: {space!r}")

        room = self.rooms[space]
        if op == "join":
            room.joined_at.setdefault(user, t)  # 重复 join 保留最早的加入时刻
        elif op == "leave":
            if user in room.joined_at:  # 没加入过的 leave 直接忽略
                room.closed_total += t - room.joined_at.pop(user)
        else:
            raise ValueError(f"unknown op: {op!r}")

    def finish(self, now):
        """把还没离开的会话临时算到 now，返回 {space: 人秒数}。不修改内部状态。"""
        if now < self.last_time:
            raise ValueError(f"time went backwards: {now} < {self.last_time}")
        return {
            space: room.closed_total + sum(now - t for t in room.joined_at.values())
            for space, room in self.rooms.items()
        }

    def top(self, k):
        """当前在线人数最多的 k 个房间，人数降序、房间名升序。"""
        counts = [(space, len(room.joined_at)) for space, room in self.rooms.items()]
        counts.sort(key=lambda item: (-item[1], item[0]))
        return counts[:k]


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    spaces = Spaces()
    spaces.event("create", "s", "", 0)
    spaces.event("join", "s", "a", 1)
    spaces.event("join", "s", "a", 2)  # 重复 join，忽略
    spaces.event("join", "s", "b", 3)
    spaces.event("leave", "s", "a", 5)  # a 在线 4 秒

    # b 从 3 到 6 还在线，算 3 秒；合计 7
    assert spaces.finish(6) == {"s": 7}
    assert spaces.top(1) == [("s", 1)]

    # finish 不入账，重复调用结果不变
    assert spaces.finish(6) == {"s": 7}

    # 错误输入
    expect_value_error(spaces.event, "join", "missing", "a", 6)
    expect_value_error(spaces.event, "join", "s", "c", 4)
    expect_value_error(spaces.event, "kick", "s", "b", 6)

    # top 按人数降序、名字升序
    spaces.event("create", "r", "", 7)
    spaces.event("create", "q", "", 7)
    spaces.event("join", "q", "x", 7)
    spaces.event("join", "q", "y", 7)
    assert spaces.top(3) == [("q", 2), ("s", 1), ("r", 0)]


if __name__ == "__main__":
    test()
