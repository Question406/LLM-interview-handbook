---
id: lc-295-find-median-from-data-stream
section: heap
order: 4
level: S
title: LC 295 · 数据流的中位数
quick: >-
  用对顶堆：大根堆 `lo` 存较小的一半，小根堆 `hi` 存较大的一半，我保持 $|lo|-|hi|\in\{0,1\}$。个数是奇数时取 `lo` 顶，偶数时取两个堆顶的平均。
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

## 题目描述

设计一个数据流容器，整数会逐个加入，容器要能随时返回当前全部数的中位数。把已有数按非递减顺序排列后，奇数个数的中位数是正中间那个数；偶数个数的中位数是中间两个数的算术平均。

### 输入与输出

实现 `MedianFinder()`、`addNum(num) -> None` 和 `findMedian() -> float`。构造时容器为空；addNum 保留重复值，findMedian 不删除数据。示例用第一行操作名、第二行对应参数列表表示连续调用，输出中的 null 表示构造或无返回值的方法。

### 约束

- `-10^5 <= num <= 10^5`。
- 调用 findMedian 时保证容器非空。
- addNum 与 findMedian 的总调用次数至多为 `5 * 10^4`。

### 示例

```text
输入：["MedianFinder", "addNum", "addNum", "findMedian", "addNum", "findMedian"]
[[], [1], [2], [], [3], []]
输出：[null, null, null, 1.5, null, 2.0]
```

[LeetCode 原题](https://leetcode.com/problems/find-median-from-data-stream/description/)

## 解题思路与参考答案

## 题意

实现 `MedianFinder`：`addNum` 加入一个整数，`findMedian` 返回当前中位数。偶数个时取中间两个数的平均。

## 思路

我会用两个堆把数据切成左右两半，中位数就在两个堆顶上。`lo` 是大根堆，放较小的一半（Python 用负数模拟）；`hi` 是小根堆，放较大的一半。开口要先把这件事讲清楚：`lo` 顶是左半最大，`hi` 顶是右半最小，`lo` 的个数等于 `hi` 或者比它多 $1$，并且 `lo` 顶 $\le$ `hi` 顶。

插入时新数先丢进 `lo`，再把 `lo` 顶移到 `hi`；如果这时 `hi` 比 `lo` 长，就再移一个回来。不管新数多大，这两条都能保住。

照测例走一遍：加 1，先进 `lo` 又被移到 `hi`，`hi` 更长再移回来，现在 `lo` 里是 1；加 2，进 `lo` 后 `lo` 顶 2 被移到 `hi`，两边各一个，中位数是 $(1+2)/2=1.5$；加 3，最后 `lo` 里是 1 和 2、`hi` 里是 3，中位数取 `lo` 顶 $2$。

每次插入都排序是 $O(n)$，用有序数组二分插入也一样慢。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
mf = MedianFinder()
mf.addNum(1)
mf.addNum(2)
assert mf.findMedian() == 1.5
mf.addNum(3)
assert mf.findMedian() == 2.0
mf2 = MedianFinder()
mf2.addNum(-1)
assert mf2.findMedian() == -1.0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

`addNum` 时间 $O(\log n)$，`findMedian` 是 $O(1)$，额外空间 $O(n)$。

## 边界

只有一个数时 `lo` 比 `hi` 多 $1$，中位数就是 `lo` 顶。全部相同时两个堆顶相等，奇偶规则照常。负数也没问题，大根堆用负数模拟，比较的还是原值，符号不会出错。偶数个取两顶平均，奇数个只取 `lo` 顶，因为 `lo` 始终不比 `hi` 短。

## 追问

**滑动窗口中位数（LC 480）怎么做？**
窗口大小 $k$ 固定，每次进一个、出一个。最省事的是用 `SortedList` 维护窗口，删旧插新都是 $O(\log k)$，写法是下面第一段。只用堆的话，难点在于堆删不了堆顶以外的元素，我会用懒删除：出窗的数字在哈希表里记一次「待删」，等它真的弹到堆顶、发现已经过期，就丢掉再弹。有效个数仍然保持 `lo` 比 `hi` 多 $0$ 或 $1$，写法是第二段。单独一张卡 `lc-480`。

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

**数据流第 $k$ 大（LC 703）和这题有什么区别？**
只要第 $k$ 大的话一个堆就够。中位数是动态的「中间」，要两个堆；第 $k$ 大只要一个容量为 $k$ 的小根堆，多出来的一律弹掉，堆顶就是答案。`add` 是 $O(\log k)$。单独一张卡 `lc-703`。

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
