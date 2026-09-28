---
id: lc-933-number-of-recent-calls
section: queue
order: 1
level: A
title: LC 933 · 最近的请求次数
quick: >-
  时间戳严格递增，用队列存请求时间。每次 `ping(t)` 先入队，再把队头小于 $t-3000$ 的全部弹出，剩下的长度就是答案。均摊
  $O(1)$，空间最多 $3001$ 个元素。
tags:
  - Queue
  - Design
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 933. Number of Recent Calls
    url: https://leetcode.com/problems/number-of-recent-calls/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

实现 `RecentCounter`：构造时计数为空；`ping(t)` 表示在时刻 $t$（毫秒）来了一个请求，返回时间区间 $[t-3000, t]$ 内的请求数（含本次）。保证每次 `ping` 的 $t$ 严格大于上一次，最多调用 $10^4$ 次。

## 思路

时间戳单调递增，过期的请求一定在最早的那一端，新请求一定加在最晚的一端，正好是队列：尾进头出。每次 `ping` 把 $t$ 入队，然后只要队头 $\lt t-3000$ 就弹出。过期的请求对之后更大的 $t$ 也一定过期，弹掉不会丢信息。

每个时间戳只入队、出队各一次，所以均摊 $O(1)$。每次都遍历全部历史去数是 $O(n)$ 一次。

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

## 复杂度

`ping` 均摊时间 $O(1)$。空间 $O(W)$，$W$ 是窗口内请求数；时间戳严格递增，最多 $3001$ 个。

## 边界

- 区间两端都包含：$t-3000$ 那个请求仍然算，所以弹出条件是严格小于。
- 两次 `ping` 相差超过 $3000$：队列被清到只剩当前一个。
- `while` 不会空队列取 `q[0]`：刚入队的 $t$ 永远不满足弹出条件。

## 追问

- **时间戳可能乱序到达？** 队列的单调前提没了。用有序结构存时间戳，查询时二分数出落在 $[t-3000, t]$ 里的个数；Python 里用 `bisect.insort` 插入是 $O(n)$，工程上会换平衡树或跳表。

```python
import bisect

class RecentCounterUnordered:
    def __init__(self):
        self.ts = []

    def ping(self, t):
        bisect.insort(self.ts, t)
        return bisect.bisect_right(self.ts, t) - bisect.bisect_left(self.ts, t - 3000)
```

- **请求量极大、同一毫秒大量并发？** 队列会很长。改成按时间分桶的环形数组：每个桶记「时间戳 + 次数」，查询时把仍在窗口里的桶加起来，空间固定为桶数，思路同 LC 362 敲击计数器。
