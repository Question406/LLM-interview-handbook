class Credits:
    """带有效期的额度账本。事件可以乱序到达，查询时按时间戳重放。

    grant 在闭区间 [start, start + duration] 内有效；扣款优先花最早到期的 grant，
    不够的部分记为债务，之后到来的 grant 先还债。
    """

    def __init__(self):
        self.events = {}  # 时间戳 -> 事件；同一时间戳只允许一个事件
        self.grant_ids = set()

    def _record(self, timestamp, event):
        if timestamp < 0:
            raise ValueError(f"timestamp must be non-negative: {timestamp}")
        if timestamp in self.events:
            raise ValueError(f"duplicate timestamp: {timestamp}")
        self.events[timestamp] = event

    def add(self, grant_id, amount, start, duration):
        if grant_id in self.grant_ids:
            raise ValueError(f"duplicate grant id: {grant_id!r}")
        if amount < 0 or duration < 0:
            raise ValueError("amount and duration must be non-negative")
        self._record(start, ("add", grant_id, amount, start + duration))
        self.grant_ids.add(grant_id)

    def subtract(self, amount, timestamp):
        if amount < 0:
            raise ValueError(f"amount must be non-negative: {amount}")
        self._record(timestamp, ("subtract", amount))

    def balance(self, timestamp):
        """返回 timestamp 时刻的可用余额；有债务或没有有效 grant 时返回 None。"""
        active = {}  # grant id -> [到期时间, 剩余额度]
        debt = 0
        for event_time, event in sorted(self.events.items()):
            if event_time > timestamp:
                break
            # 只淘汰「这个事件发生时」已经过期的 grant。
            # 一个 grant 可能先付过早期扣款、到查询时才过期，所以不能按查询时间提前丢弃。
            active = drop_expired(active, event_time)
            if event[0] == "add":
                _, grant_id, amount, end = event
                repaid = min(debt, amount)
                debt -= repaid
                active[grant_id] = [end, amount - repaid]
            else:
                debt += spend_earliest_expiring(active, event[1])

        active = drop_expired(active, timestamp)
        if debt or not active:
            return None
        return sum(remaining for _, remaining in active.values())


def drop_expired(active, now):
    """保留到期时间 >= now 的 grant（闭区间，到期那一刻仍然有效）。"""
    return {grant_id: grant for grant_id, grant in active.items() if grant[0] >= now}


def spend_earliest_expiring(active, amount):
    """按到期时间从早到晚扣 amount，原地修改 active，返回扣不完的差额。"""
    need = amount
    for grant_id in sorted(active, key=lambda gid: (active[gid][0], gid)):
        if need == 0:
            break
        paid = min(need, active[grant_id][1])
        active[grant_id][1] -= paid
        need -= paid
    return need


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 扣款先于 grant 到达：重放后结果和按时间顺序到达一样
    credits = Credits()
    credits.subtract(2, 35)
    credits.add("a", 4, 20, 40)
    credits.add("b", 3, 30, 10)
    assert credits.balance(40) == 5   # 35 时先花最早到期的 b
    assert credits.balance(41) == 4   # b 在 40 之后过期
    assert credits.balance(19) is None

    # 恰好花完但 grant 仍有效返回 0；过期后没有有效 grant 返回 None
    credits = Credits()
    credits.add("a", 4, 0, 10)
    credits.subtract(4, 5)
    assert credits.balance(10) == 0
    assert credits.balance(11) is None

    # 已过期的 a 付过早期扣款，这笔钱不能改算到 b 头上
    credits = Credits()
    credits.add("a", 4, 0, 1)
    credits.subtract(3, 1)
    credits.add("b", 10, 3, 10)
    assert credits.balance(3) == 10

    # 先透支形成债务，新 grant 先还债
    credits = Credits()
    credits.subtract(4, 1)
    assert credits.balance(1) is None
    credits.add("a", 6, 2, 10)
    assert credits.balance(2) == 2

    # 非法输入
    expect_value_error(credits.add, "a", 1, 50, 1)   # grant id 重复
    expect_value_error(credits.subtract, 1, 2)       # 时间戳重复
    expect_value_error(credits.subtract, -1, 60)     # 负金额


if __name__ == "__main__":
    test()
