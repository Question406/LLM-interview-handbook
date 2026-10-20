from bisect import bisect_left, insort
from collections import deque


class Window:
    """最近 width 秒（区间 (now - width, now]）内数值的第 k 小查询。"""

    def __init__(self, width):
        if width <= 0:
            raise ValueError("width must be positive")
        self.width = width
        self.arrivals = deque()  # 按时间排列的 (timestamp, value)，用于找出过期项
        self.sorted_values = []  # 同一组有效值的有序多重集，用于第 k 小
        self.clock = float("-inf")

    def _advance(self, now):
        """把时钟推进到 now，并删除所有 timestamp <= now - width 的项。"""
        if now < self.clock:
            raise ValueError(f"time went backwards: {now} < {self.clock}")
        self.clock = now
        while self.arrivals and self.arrivals[0][0] <= now - self.width:
            _, value = self.arrivals.popleft()
            # 只删一个相等的值，重复值不会被一起删掉
            self.sorted_values.pop(bisect_left(self.sorted_values, value))

    def add(self, timestamp, value):
        self._advance(timestamp)
        self.arrivals.append((timestamp, value))
        insort(self.sorted_values, value)

    def kth(self, now, k):
        """返回窗口内第 k 小（k 从 1 开始）；k 超出范围返回 None。"""
        self._advance(now)
        if not 1 <= k <= len(self.sorted_values):
            return None
        return self.sorted_values[k - 1]


def test():
    def expect_value_error(fn, *args):
        try:
            fn(*args)
        except ValueError:
            return
        raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

    # 重复值各自计数
    window = Window(10)
    window.add(1, 5)
    window.add(5, 2)
    window.add(5, 2)
    assert window.kth(5, 1) == 2
    assert window.kth(5, 2) == 2
    assert window.kth(5, 3) == 5
    assert window.kth(5, 0) is None

    # 左开右闭：now = 11 时 timestamp 1 已经过期，只剩两个 2
    assert window.kth(11, 2) == 2
    assert window.kth(11, 3) is None

    # now = 15 时全部过期
    assert window.kth(15, 1) is None

    # 时间不能倒退
    expect_value_error(window.add, 14, 9)
    expect_value_error(Window, 0)


if __name__ == "__main__":
    test()
