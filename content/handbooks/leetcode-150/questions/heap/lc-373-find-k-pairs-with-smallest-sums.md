---
id: lc-373-find-k-pairs-with-smallest-sums
section: heap
order: 3
level: A
title: LC 373 · 查找和最小的 K 对数字
quick: >-
  两升序数组。堆里先放 `(nums1[i], nums2[0])`，弹出后把同一 $i$ 的下一个 $j$ 推进去。时间
  $O(k\log k)$。
tags:
  - Heap
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 373. 查找和最小的 K 对数字
    url: https://leetcode.cn/problems/find-k-pairs-with-smallest-sums/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

两个升序数组 `nums1`、`nums2`，从中各取一个数组成数对，返回和最小的 $k$ 对（任意顺序，本题按弹出顺序即可）。

## 思路

最小和一定出自「某个 `nums1[i]` 配 `nums2` 的前缀」。先把至多 $k$ 个 `(nums1[i] + nums2[0], i, 0)` 入堆。弹出 `(i, j)` 后，若 $j+1$ 合法，压入 `(i, j+1)`。有序保证不会漏掉更小的、也不会把同一对加两遍。

不要枚举全部 $mn$ 对再排序。用访问集合从 $(0,0)$ 向右向下扩也行，但要去重，代码更长。

## 参考代码

```python
import heapq
from typing import List


def kSmallestPairs(nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
    heap = [(nums1[i] + nums2[0], i, 0) for i in range(min(k, len(nums1)))]
    heapq.heapify(heap)
    ans = []
    while heap and len(ans) < k:
        _, i, j = heapq.heappop(heap)
        ans.append([nums1[i], nums2[j]])
        if j + 1 < len(nums2):
            heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))
    return ans


if __name__ == "__main__":
    assert kSmallestPairs([1, 7, 11], [2, 4, 6], 3) == [[1, 2], [1, 4], [1, 6]]
    assert kSmallestPairs([1, 1, 2], [1, 2, 3], 2) == [[1, 1], [1, 1]]
    assert kSmallestPairs([1, 2], [3], 3) == [[1, 3], [2, 3]]
    print("ok")
```

## 复杂度

时间 $O(k\log k)$，堆里最多 $k$ 个候选。额外空间 $O(k)$。

## 边界

- $k$ 大于总对数：循环在堆空时停，返回全部 $mn$ 对。
- 某一侧长度为 $1$：堆里最多 $\min(k, |nums1|)$ 条「行」，每条沿 `nums2` 走到底。
- 两数组有重复：同一和可能多对，按 `(i, j)` 推进不会把同一对入堆两次。

## 追问

- **只要第 $k$ 小的和、不要列出对？** 堆弹出 $k$ 次，最后一次的和就是，时间 $O(k\log k)$。$k$ 接近 $mn$ 时改成对「和」二分：`mid` 能否作为第 $k$ 小，等价于有多少对和 $\le mid$。`nums1` 从左扫、`nums2` 从右收，计数 $O(m+n)$，二分值域 $[\mathrm{min}+\mathrm{min}, \mathrm{max}+\mathrm{max}]$，总 $O((m+n)\log W)$。

```python
def kthSmallestPairSum(nums1, nums2, k):
    lo, hi = nums1[0] + nums2[0], nums1[-1] + nums2[-1]

    def count(mid):
        cnt, j = 0, len(nums2) - 1
        for x in nums1:
            while j >= 0 and x + nums2[j] > mid:
                j -= 1
            cnt += j + 1
        return cnt

    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) < k:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

- **有序矩阵第 $k$ 小（LC 378）？** $n\times n$ 每行每列升序，本质是 $n$ 路归并。堆：先把第一列入堆，弹出后把同行下一列推进去，弹 $k$ 次，时间 $O(k\log n)$。或对值二分：`mid` 时从左下（或右上）走阶梯数有多少个 $\le mid$，与 $k$ 比，时间 $O(n\log(\max-\min))$。独立卡见 `lc-378`。

```python
def kthSmallestMatrix(matrix, k):
    n = len(matrix)
    heap = [(matrix[i][0], i, 0) for i in range(n)]
    heapq.heapify(heap)
    for _ in range(k - 1):
        _, i, j = heapq.heappop(heap)
        if j + 1 < n:
            heapq.heappush(heap, (matrix[i][j + 1], i, j + 1))
    return heap[0][0]


def kthSmallestByValue(matrix, k):
    n = len(matrix)
    lo, hi = matrix[0][0], matrix[-1][-1]
    while lo < hi:
        mid = (lo + hi) // 2
        cnt, j = 0, n - 1
        for i in range(n):
            while j >= 0 and matrix[i][j] > mid:
                j -= 1
            cnt += j + 1
        if cnt < k:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

