---
id: ali-algo-rotate-window
section: alibaba-oa
order: 39
level: A
title: 阿里手撕：旋转数组查找和滑窗最大值各用什么结构？
quick: >-
  33 我会在有序的那一半上二分。239 用单调双端队列存下标，队头过期、队尾比当前小的弹出。
tags:
  - Alibaba
  - 二分
  - 单调队列
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 搜索旋转排序数组
    url: https://leetcode.cn/problems/search-in-rotated-sorted-array/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题 / 考点说明

- 对应：LeetCode 33 / 239

33 考的是「旋转后仍有一半有序，二分要先判断哪半有序」。239 考单调队列：窗口最大值不能每步扫描 $O(nk)$。两题结构完全不同，同一轮里常当模板题连问。

## 思路

旋转查找：`mid` 与 `lo` 比，判断左半是否有序。目标落在有序半的闭区间内就收范围，否则去另一半。无重复时每次必能丢掉一半。有重复（81）`nums[lo]==nums[mid]` 时只能 `lo+=1`。

滑窗最大：双端队列保持下标对应值递减。进入 $i$ 时，队尾比 `a[i]` 小的全部弹出；队头下标 $\le i-k$ 则过期弹出。`a[q.front()]` 就是窗口最大。堆也能做但要懒删除。

## 参考代码

```python
from collections import deque
from typing import List


def search(nums: List[int], target: int) -> int:
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


def max_sliding_window(nums: List[int], k: int) -> List[int]:
    q: deque[int] = deque()
    ans: List[int] = []
    for i, x in enumerate(nums):
        while q and nums[q[-1]] < x:
            q.pop()
        q.append(i)
        if q[0] <= i - k:
            q.popleft()
        if i >= k - 1:
            ans.append(nums[q[0]])
    return ans


if __name__ == "__main__":
    assert search([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search([1], 0) == -1
    assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert max_sliding_window([1], 1) == [1]
    print("ok")
```

## 复杂度

- 33：时间 $O(\log n)$，空间 $O(1)$。有重复最坏退化为 $O(n)$。
- 239：每个下标进队出队至多一次，时间 $O(n)$，空间 $O(k)$。不要每窗口扫描 $O(nk)$。

## 边界与追问

1. 33：未旋转、单元素、目标不存在、旋转点在两端。81 有重复时相等只能收缩一端。
2. 239：$k=1$、$k=n$、窗口内单调增/减。队里存下标不是值，否则过期无法判断。
3. 追问最小值滑窗 / 堆做法：队列改递增；堆要带下标懒删除，常数更大。
