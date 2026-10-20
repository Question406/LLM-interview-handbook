---
id: lc-300-longest-increasing-subsequence
section: dp-1d
order: 5
level: S
title: LC 300 · 最长递增子序列
quick: >-
  先讲清 $dp[i]$：以 $i$ 结尾的 LIS 长度，$O(n^2)$ 枚举左侧更小的 $j$。要 $O(n\log n)$
  用 `tails`：维护各长度 LIS 的最小结尾，二分更新。
tags:
  - DP
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 300. 最长递增子序列
    url: https://leetcode.cn/problems/longest-increasing-subsequence/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

整数数组 `nums`，返回最长严格递增子序列的长度。子序列可删元素、不可改相对顺序。

## 思路

$dp[i]$ 是以 `nums[i]` 结尾的 LIS 长度。枚举 $j\lt i$ 且 `nums[j] < nums[i]`，取 $\max dp[j]+1$。答案是 $\max dp$。$O(n^2)$。

要更快：`tails[k]` 表示长度为 $k+1$ 的递增子序列里，最小的结尾值。扫到 $x$ 时二分找第一个 $\ge x$ 的位置替换（严格递增用 $\ge$）。较小的结尾更容易接上后面的数，所以替换它不会损失可达到的长度。`tails` 始终递增，长度就是答案；其中的值来自不同候选序列，并不保证能拼成原数组中的一条真实子序列。

下面写 $O(n\log n)$，$O(n^2)$ 转移放追问。

## 参考代码

```python
from typing import List


def lengthOfLIS(nums: List[int]) -> int:
    tails = []
    for x in nums:
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(tails):
            tails.append(x)
        else:
            tails[lo] = x
    return len(tails)


if __name__ == "__main__":
    assert lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert lengthOfLIS([0, 1, 0, 3, 2, 3]) == 4
    assert lengthOfLIS([7, 7, 7, 7, 7, 7, 7]) == 1
    print("ok")
```

## 复杂度

`tails`：$O(n\log n)$ 时间，$O(n)$ 空间。朴素 DP：$O(n^2)$ 时间，$O(n)$ 空间。

## 边界

- 全递减：每个新数都替换 `tails[0]`，长度 $1$。
- 全递增：每次都 append，长度 $n$。
- 有重复：严格递增，相等走「第一个 $\ge x$ 的位置替换」，不会延长。

## 追问

- **$O(n^2)$ 写法？** $dp[i]$ 是以 `nums[i]` 结尾的 LIS 长度，初值 $1$。枚举 $j\lt i$ 且 `nums[j] < nums[i]`，取 $\max dp[j]+1$。答案是 $\max dp$。先把这套转移讲清楚，再优化成 `tails`。

```python
def lengthOfLIS_n2(nums):
    n = len(nums)
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

- **打印一条 LIS？** 在 $O(n^2)$ 里同步记 `prev[i]`（从哪个 $j$ 转移来）。从 `dp` 最大的下标倒推再反转。`tails` 本身不是某条真实子序列；若坚持 $O(n\log n)$，再开 `idx`/`prev`：二分更新时记下是谁占据了该长度，并指向上一长度的下标。

```python
def reconstructLIS(nums):
    n = len(nums)
    dp = [1] * n
    prev = [-1] * n
    best = 0
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                prev[i] = j
        if dp[i] > dp[best]:
            best = i
    seq = []
    while best != -1:
        seq.append(nums[best])
        best = prev[best]
    seq.reverse()
    return seq
```
