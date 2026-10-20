import math
from threading import Lock

class Limiter:
    def __init__(self, user_capacity, user_rate, global_capacity, global_rate):
        values = (user_capacity, user_rate, global_capacity, global_rate)
        if any(not math.isfinite(v) or v <= 0 for v in values):
            raise ValueError("positive finite parameters required")
        self.uc, self.ur, self.gc, self.gr = values
        self.users = {}
        self.global_tokens = global_capacity
        self.last = None
        self.lock = Lock()

    def allow(self, user, cost, now):
        if not math.isfinite(cost) or cost <= 0 or not math.isfinite(now) or now < 0:
            raise ValueError("invalid request")
        with self.lock:
            if self.last is not None and now < self.last:
                raise ValueError("time reversed")
            if self.last is not None:
                self.global_tokens = min(self.gc, self.global_tokens + (now-self.last)*self.gr)
            self.last = now
            tokens, last = self.users.get(user, (self.uc, now))
            tokens = min(self.uc, tokens + (now-last)*self.ur)
            accepted = tokens >= cost and self.global_tokens >= cost
            if accepted:
                tokens -= cost
                self.global_tokens -= cost
            self.users[user] = (tokens, now)
            return accepted

l = Limiter(2, 1, 3, 1)
assert l.allow("a", 2, 0)
assert not l.allow("a", 1, 0)
assert l.allow("b", 1, 0)  # rejected user request did not consume global token
assert not l.allow("b", 1, 0)
assert l.allow("b", 1, 1)
assert l.allow("a", 2, 100)  # refill capped at capacity
assert not l.allow("a", 3, 100)
try: l.allow("a", 1, 99)
except ValueError: pass
else: raise AssertionError("backward clock accepted")
from concurrent.futures import ThreadPoolExecutor
l = Limiter(10, 1, 7, 1)
with ThreadPoolExecutor(8) as pool:
    assert sum(pool.map(lambda _: l.allow("u", 1, 0), range(100))) == 7
