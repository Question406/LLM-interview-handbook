---
id: lc-295-find-median-from-data-stream
section: heap
order: 4
level: S
title: LC 295 · 数据流的中位数
quick: >-
  对顶堆：大根堆 `lo` 存较小的一半，小根堆 `hi` 存较大的一半，我保持
  $|lo|-|hi|\in\{0,1\}$。奇数取 `lo` 顶，偶数取两顶平均。
tags:
  - Heap
  - Design
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 295. 数据流的中位数
    url: https://leetcode.cn/problems/find-median-from-data-stream/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

实现 `MedianFinder`：`addNum` 加入整数，`findMedian` 返回当前中位数。偶数个时取中间两个的平均。

## 思路

对顶堆。新数我先丢进 `lo`（Python 用负数模拟大根堆），再把 `lo` 顶移到 `hi`，若 `hi` 更长再移回。这样 `lo` 的个数等于 `hi` 或比它多 $1$，并且 `lo` 顶 $\le$ `hi` 顶。

排序每次插入 $O(n)$，或者用有序数组二分插入，都偏慢。开口要把「左半最大、右半最小」讲清楚。

## 参考代码

```python
import heapq


class MedianFinder:
    def __init__(self):
        self.lo = []
        self.hi = []

    def addNum(self, num: int) -> None:
        heapq.heappush(self.lo, -num)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def findMedian(self) -> float:
        if len(self.lo) > len(self.hi):
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2.0


if __name__ == "__main__":
    mf = MedianFinder()
    mf.addNum(1)
    mf.addNum(2)
    assert mf.findMedian() == 1.5
    mf.addNum(3)
    assert mf.findMedian() == 2.0
    mf2 = MedianFinder()
    mf2.addNum(-1)
    assert mf2.findMedian() == -1.0
    print("ok")
```

## 复杂度

`addNum` 时间 $O(\log n)$，`findMedian` $O(1)$。额外空间 $O(n)$。

## 边界

- 只有一个数：`lo` 比 `hi` 多 $1$，中位数就是 `lo` 顶。
- 全相同：两堆顶相等，奇偶规则照旧。
- 负数：大根堆用负数模拟，比较的是原值，符号没问题。
- 偶数 / 奇数个：偶数两顶平均，奇数只取 `lo` 顶（`lo` 始终不短于 `hi`）。

## 追问

- **滑动窗口中位数（LC 480）？** 窗口大小 $k$ 固定，每次进一个、出一个。堆不能直接删堆顶以外的元素，我会用懒删除：出窗数字在哈希表记一次「待删」，真正弹出堆顶时若已过期就丢掉再弹。有效个数仍保持 `lo` 比 `hi` 多 $0$ 或 $1$。也可以用 `SortedList` 维护窗口，删旧插新都 $O(\log k)$。独立卡见 `lc-480`。

```python
from sortedcontainers import SortedList

def medianSlidingWindow(nums, k):
    win = SortedList(nums[:k])
    ans = []
    def med():
        if k % 2:
            return float(win[k // 2])
        return (win[k // 2 - 1] + win[k // 2]) / 2.0
    ans.append(med())
    for i in range(k, len(nums)):
        win.remove(nums[i - k])
        win.add(nums[i])
        ans.append(med())
    return ans
```

```python
def medianSlidingWindowLazy(nums, k):
    lo, hi, delay = [], [], {}
    sz_lo = sz_hi = 0

    def prune(h, sign):
        while h and delay.get(sign * h[0], 0):
            x = sign * heapq.heappop(h)
            delay[x] -= 1

    def balance():
        nonlocal sz_lo, sz_hi
        if sz_lo > sz_hi + 1:
            heapq.heappush(hi, -heapq.heappop(lo))
            sz_lo -= 1
            sz_hi += 1
            prune(lo, -1)
        elif sz_lo < sz_hi:
            heapq.heappush(lo, -heapq.heappop(hi))
            sz_hi -= 1
            sz_lo += 1
            prune(hi, 1)

    def add(x):
        nonlocal sz_lo, sz_hi
        if not lo or x <= -lo[0]:
            heapq.heappush(lo, -x)
            sz_lo += 1
        else:
            heapq.heappush(hi, x)
            sz_hi += 1
        balance()

    def remove(x):
        nonlocal sz_lo, sz_hi
        delay[x] = delay.get(x, 0) + 1
        if lo and x <= -lo[0]:
            sz_lo -= 1
            if x == -lo[0]:
                prune(lo, -1)
        else:
            sz_hi -= 1
            if hi and x == hi[0]:
                prune(hi, 1)
        balance()

    for x in nums[:k]:
        add(x)
    ans = [float(-lo[0]) if k % 2 else (-lo[0] + hi[0]) / 2.0]
    for i in range(k, len(nums)):
        add(nums[i])
        remove(nums[i - k])
        ans.append(float(-lo[0]) if k % 2 else (-lo[0] + hi[0]) / 2.0)
    return ans
```

- **第 $k$ 大数据流（LC 703）？** 中位数是动态的「中间」，要两堆。只要第 $k$ 大：一个容量 $k$ 的小根堆就够，多出来的一律弹掉，堆顶就是答案。`add` 是 $O(\log k)$。独立卡见 `lc-703`。

```python
class KthLargest:
    def __init__(self, k, nums):
        self.k, self.heap = k, nums[:]
        heapq.heapify(self.heap)
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]
```
