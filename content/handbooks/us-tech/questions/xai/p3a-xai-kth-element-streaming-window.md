---
id: p3a-xai-kth-element-streaming-window
section: xai
order: 611
level: A
title: "xAI：有限内存时间窗第 k 大/小"
quick: "静态数组用 quickselect 或有界堆；最近 N 秒的时间窗要用时间队列删过期项、用有序多重集查第 k 小，固定内存下只能做近似。"
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · kth-element-streaming-window"
    url: https://www.1point3acres.com/interview/problems/company/xai/kth-element-streaming-window
    type: secondary
---

## 题目

先在一个静态数组里找第 k 大（或第 k 小）的元素，然后扩展到数据流：数据带时间戳持续到达，要求随时查询最近 N 秒内数据的第 k 小，并讨论内存有限时怎么办。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站把它收录为面经题型，不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

静态版本用 quickselect（平均 O(n)）或者大小为 k 的堆（O(n log k)）。

时间窗版本的难点是元素会过期。精确解需要两样东西同时维护同一组有效元素：

- 一个按到达时间排列的队列，用来从左边弹出过期的项；
- 一个按值排序、允许重复的结构，用来回答第 k 小。

过期时从有序结构里删掉对应的值。如果值域小（例如 0 到 1000 的整数），可以用计数桶或 Fenwick 树按前缀和找第 k 个；值域任意时用有序多重集或顺序统计树。

和面试官确认几件事：窗口边界是开还是闭；时间戳是否单调；k 越界时返回什么。最后一问「固定内存」要说清楚：值域任意、输入速率任意、内存又固定时，没办法保证精确答案，只能换成近似分位数结构（例如 t-digest、KLL sketch），并说明误差。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Window(width)`：时间窗宽度 `width > 0`，窗口是左开右闭区间 $(now - width, now]$。
- `add(timestamp, value)`：加入一个带时间戳的整数。
- `kth(now, k)`：返回当前窗口内第 k 小的值，k 从 1 开始；k 超出范围返回 `None`。
- 所有操作的时间单调不减，时间倒退抛 `ValueError`。过期的值立即丢弃。窗口内最多 $10^{4}$ 项，值为任意整数。
- 要求精确解，空间 O(窗口内项数)，不承诺与输入速率无关的固定内存。

### 输入输出示例

```text
w = Window(10)
w.add(1, 5); w.add(5, 2); w.add(5, 2)
w.kth(5, 3)   -> 5
w.kth(11, 2)  -> 2       # timestamp 1 已在 (1, 11] 之外
w.kth(11, 3)  -> None    # 窗口里只剩两个 2
w.kth(15, 1)  -> None    # 全部过期
```

### 解题思路与正确性

时间队列和有序列表始终保存完全相同的一组有效元素：加入时两边各加一份，过期时两边各删一份。删除有序列表时用 `bisect_left` 找到一个相等的值只删一次，所以重复值不会被一起删掉。

每次 `add` 和 `kth` 都先把时钟推进到当前时间、清掉过期项，再做操作。这样无论哪种操作，看到的窗口边界都是同一个 $(now - width, now]$。

### 完整参考实现（Python 3）

```python
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
```

### 可执行测试

```python
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
```

### 复杂度与追问

设窗口内有 n 项。Python 列表的插入和删除要移动元素，是 O(n)；查询第 k 小是 O(1)；空间 O(n)。每个元素只会入队、出队各一次。

- 想把更新降到 O(log n)：换成平衡的顺序统计树，或者 `sortedcontainers.SortedList`。
- 值是小范围整数：用 Fenwick 树记每个值的出现次数，更新 O(log V)，查第 k 小用树上二分，也是 O(log V)。
- 要求固定内存：精确答案做不到，改用近似分位数 sketch，并和面试官约定可接受的误差（例如排名误差不超过 εn）。
