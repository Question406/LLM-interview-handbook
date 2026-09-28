---
id: ali-algo-kth-largest
section: alibaba-oa
order: 33
level: A
title: 阿里手撕：第 K 大用堆还是快选？线上 Top-K 怎么说？
quick: >-
  我会用大小为 $k$ 的小顶堆，平均 $O(n\log k)$。快选平均 $O(n)$，最坏 $O(n^2)$，主元一定要随机。线上我更倾向堆加过期，不会对全量快排。
tags:
  - Alibaba
  - 堆
  - Top-K
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 数组中的第K个最大元素
    url: https://leetcode.cn/problems/kth-largest-element-in-an-array/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题 / 考点说明

- 对应：LeetCode 215；面经常接到「推荐 Top-K」

要的是第 $k$ 大，不是前 $k$ 大排好序。面试我先报两种写法：大小为 $k$ 的小顶堆、随机化快选。业务延伸：候选流无穷、要按时间衰减时，用堆 + TTL，或对分片各取 $k$ 再合并。别说「先全局排序」。

## 思路

堆：遍历数组。堆不足 $k$ 就推入；当前值比堆顶大则弹出堆顶再推入。结束时堆顶就是第 $k$ 大。空间 $O(k)$，适合流式。

快选：第 $k$ 大等价于升序下标 $n-k$。随机主元 partition，枢轴下标等于目标就返回；小于目标只搜右半，否则只搜左半。要提最坏 $O(n^2)$ 和随机化。

线上无限流、过期、分片，我站堆这边；快选要随机访问整段数组，不适合流。

## 参考代码

```python
from __future__ import annotations

import heapq
import random
from typing import List


def find_kth_largest_heap(nums: List[int], k: int) -> int:
    heap: List[int] = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    return heap[0]


def find_kth_largest_quickselect(nums: List[int], k: int) -> int:
    target = len(nums) - k
    lo, hi = 0, len(nums) - 1

    def partition(left: int, right: int) -> int:
        pivot_idx = random.randint(left, right)
        nums[pivot_idx], nums[right] = nums[right], nums[pivot_idx]
        pivot = nums[right]
        i = left
        for j in range(left, right):
            if nums[j] < pivot:
                nums[i], nums[j] = nums[j], nums[i]
                i += 1
        nums[i], nums[right] = nums[right], nums[i]
        return i

    while True:
        p = partition(lo, hi)
        if p == target:
            return nums[p]
        if p < target:
            lo = p + 1
        else:
            hi = p - 1


if __name__ == "__main__":
    random.seed(0)
    samples = [
        ([3, 2, 1, 5, 6, 4], 2, 5),
        ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4, 4),
        ([1], 1, 1),
        ([7, 7, 7], 2, 7),
    ]
    for arr, k, expect in samples:
        assert find_kth_largest_heap(arr, k) == expect
        assert find_kth_largest_quickselect(arr[:], k) == expect
    print("ok")
```

## 复杂度

- 堆：时间 $O(n\log k)$，空间 $O(k)$。
- 快选：平均 $O(n)$，最坏 $O(n^2)$；空间 $O(1)$ 额外（不含输入）。随机主元把最坏压成极低概率。
- 全排序：$O(n\log n)$，面试当反例，线上更不要。

## 边界与追问

1. $k=1$、全相同、含负数：堆和快选都要过。快选会改原数组，需要保序就先拷贝。
2. 追问「只要前 $k$ 大无序」：堆即可；要有序再对堆排序 $O(k\log k)$。
3. 追问推荐流 / 100 倍候选：分片各维护大小 $k$ 的堆再合并，带 TTL 惰性删；不要对全量快排或快选。
