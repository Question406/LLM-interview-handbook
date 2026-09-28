---
id: lc-215-kth-largest-element-in-an-array
section: heap
order: 1
level: S
title: LC 215 · 数组中的第K个最大元素
quick: >-
  我会开一个大小为 $k$ 的小根堆，堆顶就是第 $k$ 大，时间 $O(n\log k)$、额外空间 $O(k)$。也可以快选按枢纽划分，期望
  $O(n)$。
tags:
  - Heap
  - Quickselect
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 215. Kth Largest Element in an Array
    url: https://leetcode.com/problems/kth-largest-element-in-an-array/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

返回数组里第 $k$ 大的元素，按排序后的位置算，不去重。$k$ 从 $1$ 计，$1\le k\le n$。

## 思路

小根堆大小固定为 $k$：先放前 $k$ 个，后面比堆顶大就替换。堆里始终是目前见过的最大的 $k$ 个数，堆顶是其中最小的，也就是第 $k$ 大。

快选：随机枢纽，把数组分成大于、等于、小于三段，看第 $k$ 大该落在哪一段，只递归那一段。期望 $O(n)$，最坏 $O(n^2)$。白板我先写堆，再讲快选。

全排序 $O(n\log n)$ 能过，但面试一般要堆或快选。

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
    assert findKthLargest([2, 2, 2], 3) == 2
    assert findKthLargest([-1, -5, 0, 7], 4) == -5
    print("ok")
```

## 复杂度

堆：时间 $O(n\log k)$，额外空间 $O(k)$。快选：期望时间 $O(n)$，额外空间 $O(n)$（下面的三段写法开了新列表）；原地分区可做到 $O(1)$ 额外空间。

## 边界

- $k=1$：堆里只留当前最大值，每个新数若更大就替换，答案是全局最大。
- $k=n$：堆里装着全部，堆顶是最小值，也就是第 $n$ 大。
- 有重复：第 $k$ 大按出现次数计，不是去重后的第 $k$；堆和快选都自然处理重复。

## 追问

- **快选怎么写，重复值多时怎么办？** 随机选枢纽，分成大于、等于、小于三段。$k$ 落在「大于」段就只在那段继续；落在「等于」段直接返回枢纽；否则 $k$ 减去前两段长度去「小于」段找。三段划分让全相等的数组一步结束，避免两段划分在重复值上退化。

```python
import random

def quickSelect(nums, k):
    while True:
        pivot = random.choice(nums)
        big = [x for x in nums if x > pivot]
        mid = [x for x in nums if x == pivot]
        small = [x for x in nums if x < pivot]
        if k <= len(big):
            nums = big
        elif k <= len(big) + len(mid):
            return pivot
        else:
            k -= len(big) + len(mid)
            nums = small
```

- **数据流里动态第 $k$ 大（LC 703）？** 数组版扫完就结束；流式每次 `add` 后要立刻给出当前第 $k$ 大。我维护容量为 $k$ 的小根堆：新数先入堆，超过 $k$ 个就弹出堆顶。堆顶始终是第 $k$ 大，`add` 是 $O(\log k)$。

```python
import heapq

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
