---
id: p3a-openai-fault-tolerant-work-queue
section: openai
order: 613
level: A
title: "OpenAI：可靠任务队列：租约、重试、死信与依赖"
quick: "任务用 pending、running、done、dead 状态机，每次领取发新租约 token，上报只接受当前有效 token。超时按剩余次数重试或进死信，全部依赖 done 才能领取；至少一次交付仍需要业务幂等。"
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
  - title: "1Point3Acres · OpenAI · fault-tolerant-work-queue"
    url: https://www.1point3acres.com/interview/problems/company/openai/fault-tolerant-work-queue
    type: secondary
---

## 题目描述

实现一个带依赖、重试和租约的内存工作队列。worker 领取任务时获得本次租约专属 token；超时或失败后任务可重新派发，迟到的旧 worker 不能完成新租约下的任务。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `Queue.enqueue(job_id, max_attempts, depends=())`：入队。`max_attempts` 至少为 1，包含首次执行；`depends` 只能引用已经入队的任务。
- `Queue.reserve(now, lease) -> (job_id, token) | None`：按入队顺序取第一个依赖全部 done 的 pending 任务，租约到 `now + lease` 为止，`lease` 必须为正。
- `Queue.complete(job_id, token, now)` / `Queue.fail(job_id, token, now)`：上报结果，返回是否被接受。只有任务仍在 running 且 token 是当前租约的 token 才接受。
- `Queue.dlq()`：返回所有 dead 任务。
- 时间由调用方传入，必须单调不减。`now >= lease_end` 时租约失效；失败或超时后还有尝试次数就回到 pending，否则变成 dead。依赖了 dead 任务的任务保持阻塞，不会自动判失败。
- 最多 $10^4$ 个任务。

### 示例

```text
enqueue("a", max_attempts=2); enqueue("b", 1, depends=["a"])
reserve(now=0, lease=5)          -> ("a", 1)
complete("a", token=1, now=5)    -> False     # 5 >= 0 + 5，租约已失效
reserve(now=5, lease=5)          -> ("a", 2)  # 第二次尝试
complete("a", token=1, now=6)    -> False     # 旧 token
complete("a", token=2, now=6)    -> True
reserve(now=6, lease=2)          -> ("b", 3)  # a 已 done，b 解锁
```

## 解题思路与参考答案

我会先实现任务状态机，再用租约 token 拒绝旧 worker 的迟到上报。状态包括 pending（等待领取）、running（已被领取、租约有效）、done、dead（重试用完，进死信队列）。worker 领取任务时拿到一个租约，租约有截止时间；到期还没上报，任务自动退回 pending，或者在尝试次数用完时变成 dead。

## 题目

实现一个容错的任务队列，支持入队、worker 领取任务（reserve）、上报成功和上报失败。在此基础上加入租约超时、重试次数上限、死信队列，以及任务之间的 DAG 依赖。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

关键在于防止「僵尸 worker」：一个 worker 卡住、租约过期，任务被另一个 worker 重新领走，之后第一个 worker 才回来上报完成。解决办法是每次领取都发一个新的唯一 token，上报时必须带上这个 token，只有当前租约的 token 才被接受。

依赖的处理：一个任务只有在所有前置任务都 done 之后才能被领取。

有几点要和面试官对齐：

- `max_attempts` 是否包含第一次执行（这里包含）；
- 前置任务进了死信队列，后继任务是一直阻塞还是跟着失败（这里保持阻塞）；
- 租约恰好到期的那一刻算不算过期（这里算）。

还要说明交付语义：这种队列只能做到至少一次交付。worker 可能已经把活干完、却在上报前崩溃，任务会被重新执行，所以业务处理本身要幂等。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Queue.enqueue(job_id, max_attempts, depends=())`：入队。`max_attempts` 至少为 1，包含首次执行；`depends` 只能引用已经入队的任务。
- `Queue.reserve(now, lease) -> (job_id, token) | None`：按入队顺序取第一个依赖全部 done 的 pending 任务，租约到 `now + lease` 为止，`lease` 必须为正。
- `Queue.complete(job_id, token, now)` / `Queue.fail(job_id, token, now)`：上报结果，返回是否被接受。只有任务仍在 running 且 token 是当前租约的 token 才接受。
- `Queue.dlq()`：返回所有 dead 任务。
- 时间由调用方传入，必须单调不减。`now >= lease_end` 时租约失效；失败或超时后还有尝试次数就回到 pending，否则变成 dead。依赖了 dead 任务的任务保持阻塞，不会自动判失败。
- 最多 $10^4$ 个任务。

### 输入输出示例

```text
enqueue("a", max_attempts=2); enqueue("b", 1, depends=["a"])
reserve(now=0, lease=5)          -> ("a", 1)
complete("a", token=1, now=5)    -> False     # 5 >= 0 + 5，租约已失效
reserve(now=5, lease=5)          -> ("a", 2)  # 第二次尝试
complete("a", token=1, now=6)    -> False     # 旧 token
complete("a", token=2, now=6)    -> True
reserve(now=6, lease=2)          -> ("b", 3)  # a 已 done，b 解锁
```

### 解题思路与正确性

每个公开操作都先调用 `_advance(now)`，把到期的租约处理掉，再做本次操作。这样迟到的 `complete` 看到的已经是过期后的状态，会被拒绝。

token 每次 reserve 都递增，旧租约的 token 不可能等于当前 token，所以旧 worker 不能覆盖新一轮尝试的结果。

`enqueue` 只允许依赖已入队的任务，边总是从旧任务指向新任务，依赖图不会有环。

这个队列只保证任务的完成状态正确，保证不了业务副作用只发生一次，那部分要靠业务侧幂等。

### 完整参考实现（Python 3）

```python
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
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert job_id == "a"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
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
```

### 复杂度与追问

设任务数为 J、依赖边数为 E。每次操作都会扫描所有任务检查租约，`reserve` 还要检查依赖，所以 `_advance` 和 `reserve` 都是 O(J + E)；空间 O(J + E)。

- 任务很多时怎么避免每次全量扫描？租约截止时间放进最小堆，`_advance` 只弹出到期的；依赖用入度计数，前置任务 done 时把后继的计数减一，减到零就放进 ready 队列，`reserve` 直接从 ready 队列取。注意任务被重新领取后，堆里还留着旧的截止时间，弹出时要核对 token 或版本号，过时的直接丢弃。
- 多台机器共享这个队列呢？状态要放进数据库或协调服务。reserve 用条件更新（比较并交换）保证同一任务只被一个 worker 领走，时钟以服务端为准，不能信任 worker 本地时间。
