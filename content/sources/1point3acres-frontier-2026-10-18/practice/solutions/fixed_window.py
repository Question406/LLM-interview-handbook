class Limiter:
    """固定窗口限流：每个 key 在每个窗口 t // width 内最多消耗 limit 个 token。"""

    def __init__(self, limit, width):
        if limit <= 0 or width <= 0:
            raise ValueError("limit and width must be positive")
        self.limit = limit
        self.width = width
        self.usage = {}  # key -> {窗口编号: 已用 token 数}

    def allow(self, key, cost, t):
        """够用就扣量并返回 True；不够返回 False，且不扣量。t 可以乱序到达。"""
        if cost <= 0:
            raise ValueError("cost must be positive")
        if t < 0:
            raise ValueError("timestamp must be non-negative")
        windows = self.usage.setdefault(key, {})
        window = t // self.width
        used = windows.get(window, 0)
        if used + cost > self.limit:
            return False
        windows[window] = used + cost
        return True

    def reset(self, key):
        """清掉这个 key 的所有窗口记录。"""
        self.usage.pop(key, None)


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__} should raise ValueError")

    limiter = Limiter(limit=10, width=60)

    # 窗口 0 已用 3，再要 8 会超额，被拒绝且不扣量
    assert limiter.allow("a", 3, 0)
    assert not limiter.allow("a", 8, 10)

    # 正好用满 limit 是允许的；窗口 1 与窗口 0 独立计量
    assert limiter.allow("a", 7, 1)
    assert limiter.allow("a", 10, 60)

    # 乱序回到窗口 0，此时它已经用满
    assert not limiter.allow("a", 1, 59)

    # reset 清掉所有窗口，旧时间戳也按新状态计算
    limiter.reset("a")
    assert limiter.allow("a", 10, 0)

    # 不同 key 互不影响
    assert limiter.allow("b", 10, 0)

    # 非法参数
    expect_value_error(Limiter, 0, 60)
    expect_value_error(limiter.allow, "a", 0, 0)
    expect_value_error(limiter.allow, "a", 1, -1)


if __name__ == "__main__":
    test()
