---
id: lc-215-kth-largest-element-in-an-array
section: heap
order: 1
level: S
title: LC 215 · 数组中的第K个最大元素
quick: "我会开一个大小为 $k$ 的小根堆，堆顶就是第 $k$ 大，时间 $O(n\\log k)$、额外空间 $O(k)$。也可以快选按枢纽划分，期望 $O(n)$。"
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

## 题目描述

给定整数数组 nums 和合法排名 k，返回如果把整个数组按从大到小排序后位于第 k 个位置的元素值。重复值仍然各占一个位置，不能先对数组去重。

### 接口与输出

实现 `findKthLargest(nums: List[int], k: int) -> int`。k 从 1 开始：k=1 表示最大元素，k 等于数组长度时表示最小元素。

### 合法输入与约束

`1 <= k <= len(nums) <= 100000`，`-10000 <= nums[i] <= 10000`。返回元素值，不是它在原数组中的下标。

### 示例

```text
输入：nums = [3,2,1,5,6,4], k = 2
输出：5
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/kth-largest-element-in-an-array/description/)。

## 解题思路与参考答案

## 题意

返回数组里第 $k$ 大的元素，按排序后的位置算，不去重。$k$ 从 $1$ 计，$1\le k\le n$。

## 思路

我先写大小固定为 $k$ 的小根堆。先放前 $k$ 个，后面的数比堆顶大就替换掉堆顶。堆里始终是目前见过的最大的 $k$ 个数，堆顶是其中最小的，也就是第 $k$ 大。

拿 `[3,2,1,5,6,4]`、$k=2$ 走一遍：先放进 `3, 2`，堆顶 2。看到 1，比堆顶小，跳过；看到 5，换掉 2，堆里是 `3, 5`；看到 6，换掉 3，堆里是 `5, 6`；看到 4，比堆顶 5 小，跳过。答案 5。

写完堆再讲快选：随机选枢纽，把数组分成大于、等于、小于三段，看第 $k$ 大落在哪段，只往那一段继续。期望 $O(n)$，最坏 $O(n^2)$。

全排序 $O(n\log n)$ 也能过，但面试一般想看堆或快选。

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

堆的写法时间 $O(n\log k)$，额外空间 $O(k)$。快选期望时间 $O(n)$，额外空间 $O(n)$，因为下面的三段写法开了新列表；原地分区可以做到 $O(1)$ 额外空间。

## 边界

$k=1$ 时堆里只留当前最大值，新数更大就替换，答案是全局最大。

$k=n$ 时堆里装着全部元素，堆顶是最小值，也就是第 $n$ 大。

有重复值时，第 $k$ 大按出现次数计，跟去重后的第 $k$ 个不一样；堆和快选都会自然处理重复。

## 追问

**快选怎么写，重复值多时怎么办？**
随机选枢纽，分成大于、等于、小于三段。$k$ 落在「大于」段就只在那段继续；落在「等于」段直接返回枢纽；否则把 $k$ 减去前两段的长度，去「小于」段找。三段划分让全相等的数组一步结束，两段划分遇到大量重复值会退化。

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

**数据流里动态求第 $k$ 大呢（LC 703）？**
数组版扫完就结束，流式版每次 `add` 后都要马上给出当前第 $k$ 大。我维护容量为 $k$ 的小根堆：新数先入堆，超过 $k$ 个就弹出堆顶。堆顶始终是第 $k$ 大，`add` 是 $O(\log k)$。

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
