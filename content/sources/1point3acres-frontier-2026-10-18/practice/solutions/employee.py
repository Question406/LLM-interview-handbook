from dataclasses import dataclass, field


@dataclass
class Worker:
    rate: int
    pending_rate: int | None = None   # 晋升后的新工资率，下次入场才生效
    active: tuple | None = None       # 进行中的会话 (入场时间, 冻结的工资率)
    sessions: list = field(default_factory=list)  # 已结束的 (start, end, rate)
    last_time: float = float("-inf")


class Workers:
    def __init__(self):
        self.workers = {}
        self.bonuses = []  # (start, end, multiplier)，半开区间

    def add(self, worker_id, rate):
        if worker_id in self.workers or rate < 0:
            raise ValueError(f"cannot add worker {worker_id!r} with rate {rate}")
        self.workers[worker_id] = Worker(rate)

    def enter(self, worker_id, t):
        worker = self.workers[worker_id]
        if worker.active is not None or t < worker.last_time:
            raise ValueError(f"invalid enter for {worker_id!r} at {t}")
        if worker.pending_rate is not None:  # 晋升在入场这一刻一次性生效
            worker.rate = worker.pending_rate
            worker.pending_rate = None
        worker.active = (t, worker.rate)  # 工资率冻结到本次会话
        worker.last_time = t

    def leave(self, worker_id, t):
        worker = self.workers[worker_id]
        if worker.active is None or t < worker.last_time:
            raise ValueError(f"invalid leave for {worker_id!r} at {t}")
        start, rate = worker.active
        worker.sessions.append((start, t, rate))
        worker.active = None
        worker.last_time = t

    def promote(self, worker_id, new_rate):
        """登记新工资率；新的 promote 覆盖还没生效的旧值。"""
        if new_rate < 0:
            raise ValueError("rate must be non-negative")
        self.workers[worker_id].pending_rate = new_rate

    def bonus(self, start, end, multiplier):
        if end <= start or multiplier < 1:
            raise ValueError("bonus needs start < end and multiplier >= 1")
        self.bonuses.append((start, end, multiplier))

    def _multiplier_at(self, t):
        """时刻 t 生效的总倍率：所有覆盖 t 的奖金倍率相乘。"""
        product = 1
        for start, end, multiplier in self.bonuses:
            if start <= t < end:
                product *= multiplier
        return product

    def salary(self, worker_id, start, end):
        """已结束会话与 [start, end) 交集内的工资，按会话的冻结工资率乘奖金倍率。"""
        if end < start:
            raise ValueError("end must be >= start")
        total = 0
        for session_start, session_end, rate in self.workers[worker_id].sessions:
            lo = max(session_start, start)
            hi = min(session_end, end)
            if lo >= hi:
                continue
            # 奖金端点把 [lo, hi) 切成倍率不变的小段
            cuts = {lo, hi}
            for bonus_start, bonus_end, _ in self.bonuses:
                cuts.update(x for x in (bonus_start, bonus_end) if lo < x < hi)
            points = sorted(cuts)
            for left, right in zip(points, points[1:]):
                total += (right - left) * rate * self._multiplier_at(left)
        return total


def test():
    # 会话中途晋升不影响当前会话；[2, 4) 双倍：8 * 10 + 2 * 10 * 2 = 120
    workers = Workers()
    workers.add("a", 10)
    workers.enter("a", 0)
    workers.promote("a", 20)
    workers.leave("a", 10)
    workers.bonus(2, 4, 2)
    assert workers.salary("a", 0, 10) == 120

    # 下次入场才用新工资率 20
    workers.enter("a", 10)
    workers.leave("a", 12)
    assert workers.salary("a", 10, 12) == 40

    # 查询区间截断会话和奖金：[3, 4) 双倍 20 + [4, 5) 10 = 30；空区间为 0
    assert workers.salary("a", 3, 5) == 30
    assert workers.salary("a", 10, 10) == 0

    # 重叠奖金倍率相乘：[1, 2) 只有 3 倍，[2, 3) 是 2 * 3 = 6 倍
    overlap = Workers()
    overlap.add("b", 1)
    overlap.bonus(2, 4, 2)
    overlap.bonus(1, 3, 3)
    overlap.enter("b", 0)
    overlap.leave("b", 4)
    assert overlap.salary("b", 0, 4) == 1 + 3 + 6 + 2

    # 进行中的会话不计入；重复入场报错
    overlap.enter("b", 5)
    assert overlap.salary("b", 0, 100) == 12
    try:
        overlap.enter("b", 6)
    except ValueError:
        pass
    else:
        raise AssertionError("entering twice should raise ValueError")


if __name__ == "__main__":
    test()
