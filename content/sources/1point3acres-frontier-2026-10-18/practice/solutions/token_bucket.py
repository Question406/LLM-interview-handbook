from threading import Lock


class Store:
    """所有服务共用的令牌桶存储；用一把锁模拟共享存储里的原子操作。"""

    def __init__(self, capacity, rate):
        if capacity <= 0 or rate <= 0:
            raise ValueError("capacity and rate must be positive")
        self.capacity = capacity
        self.rate = rate          # 每秒补充的令牌数
        self.buckets = {}         # user -> (剩余令牌, 上次更新时刻)
        self.lock = Lock()

    def allow(self, user, cost, now):
        """令牌够就扣掉 cost 并返回 True；不够返回 False，且不扣令牌。"""
        if cost <= 0:
            raise ValueError(f"cost must be positive, got {cost}")
        if now < 0:
            raise ValueError(f"now must be non-negative, got {now}")

        # 补充、检查、扣减必须在同一个临界区里完成，否则两个请求可能都看到足够的令牌
        with self.lock:
            tokens, last = self.buckets.get(user, (self.capacity, now))  # 新用户满桶
            if now < last:
                raise ValueError(f"time went backwards for {user!r}: {now} < {last}")
            tokens = min(self.capacity, tokens + (now - last) * self.rate)
            allowed = cost <= tokens
            if allowed:
                tokens -= cost
            self.buckets[user] = (tokens, now)
            return allowed


def test():
    from concurrent.futures import ThreadPoolExecutor

    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 满桶 5 个，一次用完；同一时刻再要 1 个被拒；1 秒后补回 2 个
    store = Store(5, 2)
    assert store.allow("u", 5, 0)
    assert not store.allow("u", 1, 0)
    assert store.allow("u", 2, 1)

    # 补充不超过容量
    assert store.allow("v", 5, 100)
    assert not store.allow("v", 6, 1000)

    # 时间倒退和非法 cost
    expect_value_error(store.allow, "u", 1, 0)
    expect_value_error(store.allow, "u", 0, 5)

    # 8 个线程并发抢同一个用户的 10 个令牌，恰好 10 次成功
    store = Store(10, 1)
    with ThreadPoolExecutor(8) as pool:
        results = list(pool.map(lambda _: store.allow("u", 1, 0), range(100)))
    assert sum(results) == 10


if __name__ == "__main__":
    test()
