---
id: lc-215-kth-largest-element-in-an-array
section: heap
order: 1
level: S
title: LC 215 · 数组中的第K个最大元素
quick: >-
  我会开一个大小为 $k$ 的小根堆，存目前最大的 $k$ 个数，堆顶就是第 $k$ 大，时间 $O(n\log k)$。也可以用快选按枢纽划分，期望 $O(n)$。
tags:
  - Heap
  - Quickselect
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 215. 数组中的第K个最大元素
    url: https://leetcode.cn/problems/kth-largest-element-in-an-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定整数数组 nums 和整数 k，返回按数值从大到小排列后第 k 个位置上的元素。排名从 1 开始，重复值按其出现次数分别占据位置，并不是寻找第 k 个不同的数。

### 输入与输出

实现 `findKthLargest(nums, k) -> int`，只返回对应元素的值。

### 约束与约定

- `1 <= k <= len(nums) <= 100000`。
- 每个元素在 `[-10000,10000]`。
- 原题要求考虑不对整个数组排序的实现。

### 示例

```text
输入：nums = [3,2,1,5,6,4], k = 2
输出：5
```

示例按降序排列为 [6,5,4,3,2,1]，第 2 个数为 5。

[官方原题与完整题面](https://leetcode.com/problems/kth-largest-element-in-an-array/description/)。

## 解题思路与参考答案

## 题意

返回数组里第 $k$ 大的元素，按排序后的位置算，不是第 $k$ 个不同的值。$k$ 从 $1$ 开始数。

## 思路

我会先写小根堆，好写也不容易错，再补快选。堆里只保存目前最大的 $k$ 个元素：先放入前 $k$ 个，后面的元素只有比堆顶大才替换它。堆顶是这 $k$ 个数里最小的，也就是已处理元素中的第 $k$ 大。

拿 `[3,2,1,5,6,4]`、$k=2$ 走一遍：先放 3 和 2，堆顶是 2；1 比 2 小，跳过；5 替换 2，堆里是 3 和 5；6 替换 3，堆里是 5 和 6；4 比 5 小，跳过。最后堆顶 5 就是答案。

快选是随机选一个枢纽，大的放左边、小的放右边，看第 $k$ 大落在哪一侧。期望 $O(n)$，最坏 $O(n^2)$。全排序 $O(n\log n)$ 也能过，但面试一般想看堆或者快选。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
assert findKthLargest([3, 2, 1, 5, 6, 4], 2) == 5
assert findKthLargest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
assert findKthLargest([1], 1) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

堆的时间是 $O(n\log k)$，额外空间 $O(k)$。快选期望时间 $O(n)$，额外空间 $O(1)$（不计递归）。

## 边界

$k=1$ 时堆里只留当前最大值，每个新数更大就替换，答案是全局最大。$k=n$ 时堆里装着全部元素，堆顶是最小值，也就是第 $n$ 大。有重复时第 $k$ 大按出现次数算，不按去重后的第 $k$ 个，堆和快选都会自然处理重复。

## 追问

**第 $k$ 小呢？**
对称着来：维护大小为 $k$ 的大根堆（Python 里放负数），比堆顶小就替换，结束时堆顶就是第 $k$ 小。快选就按升序划分，目标下标改成 $k-1$。时间同样是 $O(n\log k)$ 或期望 $O(n)$。

```python
def findKthSmallest(nums, k):
    heap = [-x for x in nums[:k]]
    heapq.heapify(heap)
    for x in nums[k:]:
        if x < -heap[0]:
            heapq.heapreplace(heap, -x)
    return -heap[0]
```

**数据流里动态求第 $k$ 大（LC 703）呢？**
数组版扫完就结束，流式版每次 `add` 之后都要立刻给出当前第 $k$ 大。我维护容量为 $k$ 的小根堆：不足 $k$ 个先塞进去；满了以后只有新数 $\ge$ 堆顶才入堆并弹出旧堆顶。堆顶始终是第 $k$ 大，`add` 是 $O(\log k)$。单独一张卡 `lc-703`。

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
