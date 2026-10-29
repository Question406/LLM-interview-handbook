---
id: lc-933-number-of-recent-calls
section: queue
order: 1
level: A
title: LC 933 · 最近的请求次数
quick: >-
  时间戳严格递增，过期的请求总在最早那一端，所以用队列存请求时间。每次 `ping(t)` 先入队，再把队头小于 $t-3000$
  的全部弹出，剩下的长度就是答案。均摊 $O(1)$，空间最多 $3001$ 个元素。
tags:
  - Queue
  - Design
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 933. Number of Recent Calls
    url: 'https://leetcode.com/problems/number-of-recent-calls/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

设计一个请求计数器，记录按时间发生的请求。调用 ping(t) 代表在时刻 t 毫秒新增一个请求，随后返回闭区间 `[t-3000,t]` 内发生的请求总数，包含本次请求和恰好处于左端点的请求。

### 输入与输出

实现类 `RecentCounter`：构造器创建空计数器；`ping(t: int) -> int` 添加本次请求并返回计数。每次传入的 t 严格递增，不能把尚未发生的请求计入当前结果。

### 约束

- `1 <= t <= 10^9`。
- 最多调用 ping `10^4` 次。

### 示例

```text
输入：["RecentCounter", "ping", "ping", "ping", "ping"]
[[], [1], [100], [3001], [3002]]
输出：[null, 1, 2, 3, 3]
```

构造器输出记为 null。时刻 3001 的窗口仍包含时刻 1 的请求；时刻 3002 的窗口左端变成 2，该请求才被排除。

## 解题思路与参考答案

## 题意

实现 `RecentCounter`：构造时计数为空；`ping(t)` 表示在时刻 $t$（毫秒）来了一个请求，返回时间区间 $[t-3000, t]$ 内的请求数（含本次）。保证每次 `ping` 的 $t$ 严格大于上一次，最多调用 $10^4$ 次。

## 思路

我会用队列，尾进头出。时间戳单调递增，过期的请求一定在最早的那一端，新请求一定加在最晚的一端。每次 `ping` 把 $t$ 入队，然后只要队头 $\lt t-3000$ 就弹出。过期的请求对之后更大的 $t$ 也一定过期，弹掉不会丢信息。

每个时间戳只入队、出队各一次，所以均摊 $O(1)$。每次都遍历全部历史去数，是一次 $O(n)$。

拿示例走一遍，依次 `ping` 1、100、3001、3002。前三次窗口都还盖得住 1，返回 1、2、3。到 3002 时窗口是 $[2, 3002]$，1 被弹掉，剩 100、3001、3002，返回 3。

## 参考代码

```python
from collections import deque


class RecentCounter:
    def __init__(self) -> None:
        self.q: deque = deque()

    def ping(self, t: int) -> int:
        self.q.append(t)
        while self.q[0] < t - 3000:
            self.q.popleft()
        return len(self.q)


if __name__ == "__main__":
    rc = RecentCounter()
    assert rc.ping(1) == 1
    assert rc.ping(100) == 2
    assert rc.ping(3001) == 3
    assert rc.ping(3002) == 3
    assert rc.ping(6002) == 2
    assert rc.ping(10000) == 1

    rc2 = RecentCounter()
    assert rc2.ping(3000) == 1
    assert rc2.ping(6000) == 2
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
rc = RecentCounter()
assert rc.ping(1) == 1
assert rc.ping(100) == 2
assert rc.ping(3001) == 3
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

`ping` 均摊时间 $O(1)$。空间 $O(W)$，$W$ 是窗口内请求数；时间戳严格递增，最多 $3001$ 个。

## Edge Cases

区间两端都包含，$t-3000$ 那个请求仍然算，所以弹出条件是严格小于。

两次 `ping` 相差超过 $3000$ 时，队列会被清到只剩当前一个。

`while` 不会对空队列取 `q[0]`，因为刚入队的 $t$ 永远不满足弹出条件。

## 追问

**时间戳可能乱序到达呢？**
那队列的单调前提就没了。改用有序结构存时间戳，查询时二分数出落在 $[t-3000, t]$ 里的个数；Python 里用 `bisect.insort` 插入是 $O(n)$，工程上会换平衡树或跳表。

```python
import bisect


class RecentCounterUnordered:
    def __init__(self):
        self.ts = []

    def ping(self, t):
        bisect.insort(self.ts, t)
        return bisect.bisect_right(self.ts, t) - bisect.bisect_left(self.ts, t - 3000)
```

**请求量极大、同一毫秒大量并发呢？**
队列会很长。改成按时间分组统计的环形数组，每个桶记「时间戳 + 次数」，查询时把仍在窗口里的桶加起来，空间固定为桶数，思路同 LC 362 敲击计数器。
