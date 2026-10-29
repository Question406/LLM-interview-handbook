---
id: lc-373-find-k-pairs-with-smallest-sums
section: heap
order: 3
level: A
title: LC 373 · 查找和最小的 K 对数字
quick: >-
  把每个 `nums1[i]` 和升序的 `nums2` 配出的和看成一条有序序列，用小根堆做多路归并。堆里我先放 `(nums1[i],
  nums2[0])`，弹出后再把同一 $i$ 的下一个 $j$ 推进去，时间 $O(k\log k)$。
tags:
  - Heap
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 373. 查找和最小的 K 对数字
    url: 'https://leetcode.cn/problems/find-k-pairs-with-smallest-sums/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定两个非递减数组 nums1、nums2，从第一个数组选一个元素、第二个数组选一个元素组成数对 `[u,v]`，数对的分数是 u+v。请返回所有可组成数对中分数最小的 k 对。每个下标组合只算一次，但不同下标上的相同值可以产生值相同的数对。

### 输入与输出

实现 `kSmallestPairs(nums1: List[int], nums2: List[int], k: int) -> List[List[int]]`。每对的第一个值来自 nums1，第二个值来自 nums2；返回顺序不限。若第 k 小处分数相同，可以选取满足最小分数要求的任意合法数对。

### 约束

- 两个数组长度均为 1 到 `10^5`，且已经非递减排序。
- 元素范围为 `[-10^9,10^9]`。
- `1 <= k <= 10^4`，并保证 k 不超过两个数组长度之积。

### 示例

```text
输入：nums1 = [1,7,11], nums2 = [2,4,6], k = 3
输出：[[1,2],[1,4],[1,6]]
```

## 解题思路与参考答案

## 题意

两个升序数组 `nums1`、`nums2`，各取一个数组成数对，返回和最小的 $k$ 对。顺序随意，这题按弹出顺序就行。

## 思路

我会把它当成多路归并来做。固定 `nums1[i]` 之后，它和升序的 `nums2` 配出来的数对和也是升序的，所以每个 i 都可以看作一条有序序列，用小根堆把这些序列合起来，依次弹出的就是从小到大的数对。

具体是先把至多 $k$ 个 `(nums1[i] + nums2[0], i, 0)` 入堆。弹出 `(i, j)` 后，如果 $j+1$ 合法，就压入 `(i, j+1)`。每条序列内部有序，所以不会漏掉更小的，也不会把同一对加两遍。

拿 `[1,7,11]` 和 `[2,4,6]`、$k=3$ 走一遍：堆里先有 `1+2`、`7+2`、`11+2`；弹出 `1+2`，压入 `1+4`；弹出 `1+4`，压入 `1+6`；再弹出 `1+6`。答案是 `[[1,2],[1,4],[1,6]]`。

枚举全部 $mn$ 对再排序太慢。从 $(0,0)$ 开始用访问集合向右、向下扩也行，但要去重，代码更长。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert kSmallestPairs([1, 7, 11], [2, 4, 6], 3) == [[1, 2], [1, 4], [1, 6]]
assert kSmallestPairs([1, 1, 2], [1, 2, 3], 2) == [[1, 1], [1, 1]]
assert kSmallestPairs([1, 2], [3], 3) == [[1, 3], [2, 3]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(k\log k)$，堆里最多 $k$ 个候选，额外空间 $O(k)$。

## Edge Cases

$k$ 大于总对数时，循环在堆空时停下，返回全部 $mn$ 对。某一侧长度为 $1$ 时，堆里最多有 $\min(k, |nums1|)$ 条「行」，每条沿着 `nums2` 走到底。两个数组有重复时，同一个和可能对应多对，按 `(i, j)` 推进不会把同一对入堆两次。

## 追问

**只要第 $k$ 小的和，不用列出数对呢？**
堆弹 $k$ 次，最后一次的和就是，时间 $O(k\log k)$。$k$ 接近 $mn$ 时我会改成对「和」做二分：判断 `mid` 能不能作为第 $k$ 小，等价于数一数有多少对的和 $\le mid$。`nums1` 从左往右扫、`nums2` 从右往左收，计数是 $O(m+n)$，二分的值域是 $[\mathrm{min}+\mathrm{min}, \mathrm{max}+\mathrm{max}]$，总共 $O((m+n)\log W)$。

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

**有序矩阵里的第 $k$ 小（LC 378）呢？**
$n\times n$ 矩阵每行每列都升序，就是 $n$ 路归并。用堆的话先把第一列入堆，弹出一个就把同一行的下一列推进去，弹 $k$ 次，时间 $O(k\log n)$。也可以对值二分：给定 `mid`，从左下角（或右上角）走阶梯，数出有多少个 $\le mid$，再和 $k$ 比，时间 $O(n\log(\max-\min))$。单独一张卡 `lc-378`。

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
