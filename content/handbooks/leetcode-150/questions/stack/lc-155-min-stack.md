---
id: lc-155-min-stack
section: stack
order: 3
level: S
title: LC 155 · 最小栈
quick: >-
  主栈存值，同步一个最小值栈：入栈时压
  $\min(val, mins[-1])$，出栈两边一起弹。`getMin` 看辅助栈顶，均摊 $O(1)$。
tags:
  - Stack
  - Design
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 155. 最小栈
    url: https://leetcode.cn/problems/min-stack/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

设计支持 `push`、`pop`、`top` 以及在 $O(1)$ 取最小元素的栈。

## 思路

只靠一个栈取最小要扫，是 $O(n)$。再同步一个 `mins`：每次 `push(val)` 时压入 `min(val, mins[-1])`（空则压 `val`）。`pop` 两个栈一起弹。`getMin` 读 `mins[-1]`。当前最小值被弹出后，次小值正好露在辅助栈顶。

也可以只在 `val <= 当前最小` 时才往 `mins` 压，弹出时若 `top == getMin` 再弹 `mins`。相等也要压，否则连续两个相同最小值会丢。

## 参考代码

```python
class MinStack:
    def __init__(self) -> None:
        self.st = []
        self.mins = []

    def push(self, val: int) -> None:
        self.st.append(val)
        self.mins.append(val if not self.mins else min(val, self.mins[-1]))

    def pop(self) -> None:
        self.st.pop()
        self.mins.pop()

    def top(self) -> int:
        return self.st[-1]

    def getMin(self) -> int:
        return self.mins[-1]


if __name__ == "__main__":
    s = MinStack()
    s.push(-2)
    s.push(0)
    s.push(-3)
    assert s.getMin() == -3
    s.pop()
    assert s.top() == 0
    assert s.getMin() == -2
    print("ok")
```

## 复杂度

每次操作 $O(1)$。额外空间 $O(n)$，与主栈等长。

## 边界

- 最小值在栈底：弹出上层后 `mins` 顶仍是它。
- 最小值在栈顶：弹出后次小值露出来。
- 连续相同最小值：同步压两份，只压一次会丢。
- 负数、全相等：`min` 规则不变。

## 追问

- **$O(1)$ 额外空间？** 差值编码：栈里存 `val - min`，另用一个变量记当前最小。压入时若 $val \lt min$，压负数差值并更新 `min`；弹出时若栈顶为负，说明弹出的是旧最小值，用 `min = min - top` 恢复。取顶：栈顶为负则答案就是 `min`，否则是 `min + top`。32 位下 `val - min` 可能溢出，可读性也差，我会先讲双栈再提这一招。相等最小值也要能恢复，负数差值只在「刷新最小值」时出现。

```python
class MinStackDiff:
    def __init__(self):
        self.st = []
        self.mn = 0

    def push(self, val):
        if not self.st:
            self.st.append(0)
            self.mn = val
        else:
            self.st.append(val - self.mn)
            if val < self.mn:
                self.mn = val

    def pop(self):
        d = self.st.pop()
        if d < 0:
            self.mn -= d

    def top(self):
        return self.mn if self.st[-1] < 0 else self.mn + self.st[-1]

    def getMin(self):
        return self.mn
```

- **最大栈 / 队列取最小？** 最大栈与这题对称：辅助栈压 `max(val, maxs[-1])`。队列不能只靠一个最小值变量，因为队头弹出的不一定是最小。用单调队列：下标递增、值递增（取最小）或递减（取最大），队头就是当前窗口最值，弹出时若队头下标过期再弹。这就是滑动窗口最大值（LC 239）的结构。栈的 min 是「后缀最值」，队列的 min 是「区间最值」，别混。

```python
from collections import deque

def maxSlidingWindow(nums, k):
    dq, ans = deque(), []
    for i, x in enumerate(nums):
        while dq and nums[dq[-1]] <= x:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            ans.append(nums[dq[0]])
    return ans
```
