---
id: lc-215-kth-largest-element-in-an-array
section: heap
order: 1
level: S
title: LC 215 · 数组中的第K个最大元素
quick: >-
  小根堆只留 $k$ 个，堆顶就是第 $k$ 大。或快选按枢纽划分，期望
  $O(n)$。堆的时间 $O(n\log k)$。
tags:
  - Heap
  - Quickselect
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 215. 数组中的第K个最大元素
    url: https://leetcode.cn/problems/kth-largest-element-in-an-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

返回数组中第 $k$ 大的元素（不是第 $k$ 个不同的）。$k$ 从 $1$ 计。

## 思路

小根堆大小固定为 $k$：先放前 $k$ 个，后面比堆顶大就替换。结束时堆顶是第 $k$ 大。

快选：随机枢纽，大的在左、小的在右，看第 $k$ 大应落在哪一侧。期望 $O(n)$，最坏 $O(n^2)$。面试先写堆，再讲快选。

全排序 $O(n\log n)$ 能过，但不是目标写法。

## 参考代码

```python
import heapq
from typing import List


def findKthLargest(nums: List[int], k: int) -> int:
    heap = nums[:k]
    heapq.heapify(heap)
    for x in nums[k:]:
        if x > heap[0]:
            heapq.heapreplace(heap, x)
    return heap[0]


if __name__ == "__main__":
    assert findKthLargest([3, 2, 1, 5, 6, 4], 2) == 5
    assert findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
    assert findKthLargest([1], 1) == 1
    print("ok")
```

## 复杂度

堆：时间 $O(n\log k)$，额外空间 $O(k)$。快选：期望时间 $O(n)$，额外空间 $O(1)$（不计递归）。

## 边界

- $k=1$：堆里只留当前最大值，每个新数若更大就替换，答案是全局最大。
- $k=n$：堆里装着全部，堆顶是最小值，即第 $n$ 大。
- 有重复：第 $k$ 大按出现次数计，不是去重后的第 $k$；堆和快选都自然处理重复。

## 追问

- **第 $k$ 小？** 对称：固定大小 $k$ 的大根堆（Python 放负数），比堆顶小就替换，结束时堆顶是第 $k$ 小。快选则按升序划分，目标下标改成 $k-1$。时间同样 $O(n\log k)$ 或期望 $O(n)$。

```python
def findKthSmallest(nums, k):
    heap = [-x for x in nums[:k]]
    heapq.heapify(heap)
    for x in nums[k:]:
        if x < -heap[0]:
            heapq.heapreplace(heap, -x)
    return -heap[0]
```

- **数据流里动态第 $k$ 大（LC 703）？** 数组版扫完就结束；流式每次 `add` 后要立刻给出当前第 $k$ 大。维护容量为 $k$ 的小根堆：不足 $k$ 个先塞；满了只有新数 $\ge$ 堆顶才入堆并弹出旧顶。堆顶始终是第 $k$ 大。`add` 为 $O(\log k)$。独立卡见 `lc-703`。

```python
class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = nums[:]
        heapq.heapify(self.heap)
        while len(self.heap) > k:
            heapq.heappop(self.heap)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]
```

