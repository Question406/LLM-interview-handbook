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


def test():
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


if __name__ == "__main__":
    test()
