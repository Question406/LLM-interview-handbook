from dataclasses import dataclass


@dataclass
class Job:
    max_attempts: int
    depends_on: tuple
    state: str = "pending"  # pending / running / done / dead
    attempts: int = 0       # 含首次执行
    token: int = None       # 当前租约的 token，每次 reserve 都换新
    lease_end: float = None


class Queue:
    """带租约、重试、死信和依赖的任务队列。调用方传入的 now 必须单调不减。"""

    def __init__(self):
        self.jobs = {}  # job id -> Job，dict 保持入队顺序
        self.last_token = 0
        self.clock = float("-inf")

    def _advance(self, now):
        """推进时钟，把租约到期（now >= lease_end）的任务退回 pending 或判 dead。"""
        if now < self.clock:
            raise ValueError(f"time went backwards: {now} < {self.clock}")
        self.clock = now
        for job in self.jobs.values():
            if job.state == "running" and now >= job.lease_end:
                self._retry_or_kill(job)

    @staticmethod
    def _retry_or_kill(job):
        job.state = "dead" if job.attempts >= job.max_attempts else "pending"

    def enqueue(self, job_id, max_attempts, depends=()):
        """只能依赖已经入队的任务，所以依赖图天然无环。"""
        if job_id in self.jobs:
            raise ValueError(f"duplicate job id: {job_id!r}")
        if max_attempts < 1:
            raise ValueError(f"max_attempts must be at least 1: {max_attempts}")
        missing = [dep for dep in depends if dep not in self.jobs]
        if missing:
            raise ValueError(f"unknown dependencies: {missing}")
        self.jobs[job_id] = Job(max_attempts=max_attempts, depends_on=tuple(depends))

    def reserve(self, now, lease):
        """按入队顺序取第一个依赖全部 done 的 pending 任务，返回 (job_id, token)；没有则 None。"""
        if lease <= 0:
            raise ValueError(f"lease must be positive: {lease}")
        self._advance(now)
        for job_id, job in self.jobs.items():
            if job.state == "pending" and self._dependencies_done(job):
                self.last_token += 1
                job.state = "running"
                job.token = self.last_token
                job.lease_end = now + lease
                job.attempts += 1
                return job_id, job.token
        return None

    def _dependencies_done(self, job):
        return all(self.jobs[dep].state == "done" for dep in job.depends_on)

    def _finish(self, job_id, token, now, success):
        self._advance(now)  # 先让过期租约失效，迟到的完成通知才会被拒绝
        job = self.jobs.get(job_id)
        # 只有当前租约的 token 能提交结果，旧 worker 的通知一律无效
        if job is None or job.state != "running" or job.token != token:
            return False
        if success:
            job.state = "done"
        else:
            self._retry_or_kill(job)
        return True

    def complete(self, job_id, token, now):
        return self._finish(job_id, token, now, success=True)

    def fail(self, job_id, token, now):
        return self._finish(job_id, token, now, success=False)

    def dlq(self):
        """返回所有 dead 任务的 id（死信队列）。"""
        return [job_id for job_id, job in self.jobs.items() if job.state == "dead"]


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 租约在 now >= lease_end 时失效，旧 token 永远不能完成新租约
    queue = Queue()
    queue.enqueue("a", 2)
    queue.enqueue("b", 1, ["a"])
    job_id, first_token = queue.reserve(0, 5)
    assert job_id == "a"
    assert not queue.complete("a", first_token, 5)   # 恰好到期，已经失效
    _, second_token = queue.reserve(5, 5)
    assert not queue.complete("a", first_token, 6)
    assert queue.complete("a", second_token, 6)

    # 依赖 done 之后，后继任务才能被取走
    assert queue.reserve(6, 2)[0] == "b"

    # 超时用完尝试次数后进入死信队列
    queue = Queue()
    queue.enqueue("x", 1)
    queue.reserve(0, 1)
    assert queue.reserve(1, 1) is None
    assert queue.dlq() == ["x"]

    # fail 后还有尝试次数就重新排队
    queue = Queue()
    queue.enqueue("y", 2)
    _, token = queue.reserve(0, 10)
    assert queue.fail("y", token, 1)
    assert queue.reserve(2, 10)[0] == "y"

    # 非法输入
    expect_value_error(queue.enqueue, "z", 1, ["missing"])
    expect_value_error(queue.enqueue, "y", 1)
    expect_value_error(queue.reserve, 1, 5)          # 时间倒退


if __name__ == "__main__":
    test()
