---
id: lc-155-min-stack
section: stack
order: 3
level: S
title: LC 155 · 最小栈
quick: >-
  主栈存值，再同步一个最小值栈：每次入栈压 $\min(val, mins[-1])$，出栈两边一起弹。`getMin` 直接看辅助栈顶，均摊
  $O(1)$，代价是和主栈等长的额外空间。
tags:
  - Stack
  - Design
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 155. 最小栈
    url: 'https://leetcode.cn/problems/min-stack/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

设计一个栈，除了普通的入栈、出栈和查看栈顶，还能随时查询当前栈内的最小值。重复的值可以多次入栈，出栈时每次只移除一个栈顶元素，最小值也要反映移除后的当前内容。

### 输入与输出

实现 `MinStack()`、`push(val) -> None`、`pop() -> None`、`top() -> int` 和 `getMin() -> int`。top 与 getMin 只查看，不删除元素。要求每个操作的时间为 O(1)。示例的操作名列表和参数列表逐项对应，null 表示构造或无返回值的操作。

### 约束

- `-2^31 <= val <= 2^31 - 1`。
- 调用 pop、top、getMin 时保证栈非空。
- 所有方法调用总数至多为 `3 * 10^4`。

### 示例

```text
输入：["MinStack","push","push","push","getMin","pop","top","getMin"]
[[],[-2],[0],[-3],[],[],[],[]]
输出：[null,null,null,null,-3,null,0,-2]
```

[LeetCode 原题](https://leetcode.com/problems/min-stack/description/)

## 解题思路与参考答案

## 题意

设计支持 `push`、`pop`、`top` 以及在 $O(1)$ 取最小元素的栈。

## 思路

我会用两个栈：主栈存值，另一个栈 `mins` 和它同步，记「到这一层为止的最小值」。只靠一个栈取最小要扫一遍，是 $O(n)$。

每次 `push(val)` 往 `mins` 压 `min(val, mins[-1])`，`mins` 为空就压 `val`。`pop` 两个栈一起弹，`getMin` 读 `mins[-1]`。这样当前最小值被弹出以后，次小值正好露在辅助栈顶。

拿样例走一下。依次压 $-2$、$0$、$-3$，`mins` 是 `[-2, -2, -3]`，`getMin` 返回 $-3$。弹一次以后，主栈顶变成 $0$，`mins` 顶变回 $-2$。

还有一种省一点空间的写法：只在 `val <= 当前最小` 时才往 `mins` 压，弹出时如果 `top == getMin` 再弹 `mins`。相等也要压，否则连续两个相同的最小值会丢一个。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
s = MinStack()
s.push(-2)
s.push(0)
s.push(-3)
assert s.getMin() == -3
s.pop()
assert s.top() == 0
assert s.getMin() == -2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

每次操作 $O(1)$。额外空间 $O(n)$，与主栈等长。

## Edge Cases

最小值在栈底时，弹掉上层，`mins` 顶仍然是它。最小值在栈顶时，弹出后次小值露出来。

连续出现相同的最小值，同步写法会各压一份；用「只在更小时压」的写法，相等也得压，只压一次会丢。

负数、全相等都按同一个 `min` 规则处理。

## 追问

**要 $O(1)$ 额外空间呢？**
可以用差值编码：栈里存 `val - min`，另用一个变量记当前最小。压入时如果 $val \lt min$，压进去的差值是负数，同时更新 `min`；弹出时栈顶为负，说明弹出的是旧最小值，用 `min = min - top` 恢复。取栈顶时，栈顶为负答案就是 `min`，否则是 `min + top`。负数差值只在刷新最小值时出现，所以相等的最小值也能正确恢复。缺点是 32 位下 `val - min` 可能溢出，可读性也差，我会先讲双栈，再提这一招。

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

**最大栈，或者队列取最小呢？**
最大栈和这题对称，辅助栈压 `max(val, maxs[-1])` 就行。队列没法只靠一个最小值变量，因为队头弹出的不一定是最小。要用单调队列：下标递增，值递增（取最小）或递减（取最大），队头就是当前窗口的最值，队头下标过期时再弹掉。这就是滑动窗口最大值（LC 239）的结构。栈的 min 是「后缀最值」，队列的 min 是「区间最值」，两者别混。

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
