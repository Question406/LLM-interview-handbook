---
id: ali-algo-kth-largest
section: alibaba-oa
order: 33
level: A
title: 阿里手撕：第 K 大用堆还是快选？线上 Top-K 怎么说？
quick: "我会用大小为 $k$ 的小顶堆，时间 $O(n\\log k)$，适合流式；快选平均 $O(n)$、最坏 $O(n^2)$，主元一定要随机。线上 Top-K 我更倾向堆加过期，分片各取 $k$ 再合并，不会对全量快排。"
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

## 题目描述

给定一个整数数组与整数 k，返回数组中按从大到小排序后位于第 k 位的元素。重复值按出现次数参与排名，不是求第 k 个不同的数。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `find_kth_largest_heap(nums, k)` 和 `find_kth_largest_quickselect(nums, k)`；`nums` 是非空整数列表，`1 <= k <= len(nums)`。

### 输出与约束

两个接口均返回该元素的数值，不返回下标或前 k 个元素。快选版本允许改动传入列表；需要保留原顺序时调用者自行传入副本。

### 示例

```text
输入：nums = [3, 2, 1, 5, 6, 4], k = 2
输出：5
输入：nums = [7, 7, 7], k = 2
输出：7
```

## 解题思路与参考答案

## 真题 / 考点说明

- 对应：LeetCode 215；面经常接到「推荐 Top-K」

我会先报两种写法：大小为 $k$ 的小顶堆，和随机化快选。题目要的是第 $k$ 大，不用把前 $k$ 大排好序。延伸到业务上，候选流无穷、还要按时间衰减，我会用堆 + TTL，或者对分片各取 $k$ 再合并，「先全局排序」这种话别说。

## 思路

堆的做法是遍历数组：堆里不足 $k$ 个就推入；当前值比堆顶大，就弹出堆顶再推入。遍历完，堆顶就是第 $k$ 大。比如 `[3, 2, 1, 5, 6, 4]` 取第 2 大，堆里最后留下 5 和 6，堆顶 5 就是答案。空间只要 $O(k)$，适合流式。

快选利用第 $k$ 大等价于升序下标 $n-k$。随机选主元做 partition，枢轴下标等于目标就返回；比目标小就只搜右半，否则只搜左半。要主动提最坏 $O(n^2)$ 和为什么要随机化。

线上遇到无限流、过期、分片，我站堆这边；快选要随机访问整段数组，不适合流。

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

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert find_kth_largest_heap(arr, k) == expect` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 复杂度

堆的时间 $O(n\log k)$，空间 $O(k)$。快选平均 $O(n)$，最坏 $O(n^2)$，额外空间 $O(1)$（不含输入），随机主元把最坏情况压成极低概率。全排序是 $O(n\log n)$，面试里拿来当反例，线上更不要用。

## 追问

**要测哪些边界？**
$k=1$、全相同、含负数，堆和快选都要过。快选会改原数组，需要保序就先拷贝。

**只要前 $k$ 大、不要求有序呢？**
堆就够了；要有序，再对堆排序，$O(k\log k)$。

**推荐流、候选扩大 100 倍怎么办？**
分片各维护大小为 $k$ 的堆再合并，带 TTL 惰性删；不要对全量快排或快选。
