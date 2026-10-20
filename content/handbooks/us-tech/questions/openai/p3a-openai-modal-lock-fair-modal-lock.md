---
id: p3a-openai-modal-lock-fair-modal-lock
section: openai
order: 625
level: A
title: "OpenAI：ModalLock：同模式并发与跨模式公平"
quick: "用一个条件变量保护当前 mode、持有者数和 FIFO 等待队列，循环重查进入条件；公平版只放行队首那组同 mode 请求，防止同 mode 无限插队。"
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
  - title: "1Point3Acres · OpenAI · modal-lock-fair-modal-lock"
    url: https://www.1point3acres.com/interview/problems/company/openai/modal-lock-fair-modal-lock
    type: secondary
---

## 题目

实现一个「模式锁」ModalLock：每次加锁带一个 mode，同一个 mode 的多个线程可以同时持有，不同 mode 之间互斥（类似读写锁，但模式可以有任意多种）。第二问加公平性：等待的请求要按到达顺序成组放行，不能让某个模式一直插队把别的模式饿死。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

用一个条件变量保护三样状态：当前持有的 mode、持有者数量、等待队列。线程能进入的条件是「没人持有，或者持有的正好是我的 mode」。等待一定要写成循环重查条件（Python 里用 `wait_for`），因为被唤醒时条件不一定成立：可能是虚假唤醒，也可能被别的线程抢先改了状态。

非公平版本的问题是饥饿：只要 A 模式的线程源源不断，持有者数就一直不归零，排队的 B 永远进不去。公平版本的做法是让每个请求先进入 FIFO 队列，只有当排在自己前面的等待者全都是同一个 mode 时才能进入。这样：

- 新来的 A 发现前面有 B 在等，就排到 B 后面，不会无限插队；
- 队首连续的一组同 mode 请求可以一起进入，不需要逐个串行。

还要注意唤醒的时机：最后一个持有者离开时要唤醒等待者；一个线程进入后也要唤醒一次，因为同组后面的等待者现在可能也满足条件了。释放要放在 `finally` 里，保证异常路径也会释放。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `ModalLock(fair=False)`：`fair=True` 时启用按到达顺序成组放行。
- `acquire(mode)` / `release(mode)`：同 mode 可并发，不同 mode 互斥。未持有该 mode 就 `release` 抛 `RuntimeError`。
- `hold(mode)`：上下文管理器，异常时也释放。
- `fair=True` 时，等待请求按连续的同 mode 组 FIFO 放行；已有异 mode 请求在等时，后来的同 mode 请求不能插队。
- mode 是可比较的字符串。锁不记录持有者身份，也不支持重入、等待取消和超时。最多 100 个线程。

### 输入输出示例

```text
线程 1、2 先后 acquire("A")        -> 两个都立即进入
A 持有中，线程 3 acquire("B")       -> 排队
随后线程 4 acquire("A")             -> fair=True 时排在 B 后面
所有 A 释放                          -> B 先进入，B 释放后线程 4 的 A 才进入
```

### 解题思路与正确性

所有检查和状态修改都在同一个 `Condition` 的锁里完成，所以「判断能否进入」和「登记成持有者」之间不会被其他线程打断。

互斥：线程进入时要么没有持有者，要么持有的 mode 和自己相同，所以任何时刻持有者都属于同一个 mode。

公平：进入条件要求自己前面的等待者都和自己同 mode，也就是自己属于队首那一组。队首组进入后从队列移除，下一组成为队首；只要持有者最终会释放，每一组都会轮到，不会饿死。同一组的线程只要队首是它们这个 mode 就能同时通过，不会被不必要地串行化。

### 完整参考实现（Python 3）

```python
from contextlib import contextmanager
from threading import Condition


class ModalLock:
    """同一 mode 可以同时持有，不同 mode 互斥。fair=True 时按到达顺序成组放行。"""

    def __init__(self, fair=False):
        self.cond = Condition()
        self.mode = None    # 当前持有的 mode；没人持有时为 None
        self.holders = 0    # 当前 mode 的持有者数
        self.waiting = []   # 按到达顺序排队的 (ticket, mode)
        self.fair = fair

    def _can_enter(self, ticket, mode):
        if self.holders and self.mode != mode:
            return False
        if not self.fair:
            return True
        # 公平模式：排在我前面的等待者必须全是同一个 mode，
        # 也就是我属于队首那一组；否则前面有异 mode 在等，不能插队
        for queued_ticket, queued_mode in self.waiting:
            if queued_ticket is ticket:
                return True
            if queued_mode != mode:
                return False
        return False

    def acquire(self, mode):
        ticket = object()
        with self.cond:
            self.waiting.append((ticket, mode))
            self.cond.wait_for(lambda: self._can_enter(ticket, mode))  # 循环重查，防虚假唤醒
            self.waiting.remove((ticket, mode))
            self.mode = mode
            self.holders += 1
            self.cond.notify_all()  # 同组后面的等待者现在可能也能进来

    def release(self, mode):
        with self.cond:
            if not self.holders or self.mode != mode:
                raise RuntimeError(f"release({mode!r}) without holding it")
            self.holders -= 1
            if self.holders == 0:
                self.mode = None
            self.cond.notify_all()

    @contextmanager
    def hold(self, mode):
        self.acquire(mode)
        try:
            yield
        finally:
            self.release(mode)  # 异常路径也释放
```

### 可执行测试

```python
from threading import Event, Thread

def wait_until_queued(lock, count):
    """等到排队人数达到 count，不靠 sleep 猜测线程调度。"""
    with lock.cond:
        assert lock.cond.wait_for(lambda: len(lock.waiting) >= count, timeout=2)

# 同 mode 可以并发持有
lock = ModalLock(fair=True)
lock.acquire("A")
second_a = Event()

def acquire_a_again():
    lock.acquire("A")
    second_a.set()

thread = Thread(target=acquire_a_again)
thread.start()
assert second_a.wait(2)
thread.join()
lock.release("A")
lock.release("A")
assert lock.holders == 0

# 公平模式：A 持有时 B 排队，后来的 A 不能越过 B
lock = ModalLock(fair=True)
order = []
lock.acquire("A")

def worker(mode):
    with lock.hold(mode):
        order.append(mode)

b_thread = Thread(target=worker, args=("B",))
b_thread.start()
wait_until_queued(lock, 1)
late_a = Thread(target=worker, args=("A",))
late_a.start()
wait_until_queued(lock, 2)
assert order == []  # 两个都还在等
lock.release("A")
b_thread.join(2)
late_a.join(2)
assert order == ["B", "A"]

# 异常路径也会释放
try:
    with lock.hold("C"):
        raise ValueError("boom")
except ValueError:
    pass
assert lock.holders == 0
assert lock.mode is None

# 没持有就释放是错误
try:
    lock.release("A")
except RuntimeError:
    pass
else:
    raise AssertionError("release without acquire should raise")
```

### 复杂度与追问

设等待线程数为 W。公平模式下每次检查进入条件要扫描队列，O(W)；`release` 的状态更新是 O(1)，但 `notify_all` 会唤醒所有等待者，每个都要重新检查一遍。空间 O(W)。

- 支持取消或超时：等待超时后必须把自己从队列里删掉，并 `notify_all`，否则后面的线程会一直认为前面还有异 mode 在等。
- 减少无效唤醒：给每个 mode 组单独一个条件变量，只唤醒队首那一组。
- 这份实现不检查是哪个线程在释放，任何线程都可以 `release`。要防误用，可以记录每个持有线程的 id，`release` 时校验。
