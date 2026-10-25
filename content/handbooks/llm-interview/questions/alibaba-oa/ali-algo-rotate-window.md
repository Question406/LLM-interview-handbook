---
id: ali-algo-rotate-window
section: alibaba-oa
order: 39
level: A
title: 阿里手撕：旋转数组查找和滑窗最大值各用什么结构？
quick: >-
  旋转数组查找（33）先判断哪一半有序，目标落在有序那半的范围里就往那边收，否则去另一半。滑窗最大值（239）用存下标的单调递减双端队列：移除过期的队头，把队尾比当前值小的弹出，队头就是当前最大值的位置。
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

## 题目描述

本卡分别要求实现旋转有序数组查找与固定窗口最大值，两者是独立接口。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

`search(nums, target)`：nums 由互不相同的整数升序数组在某个位置旋转得到。`max_sliding_window(nums, k)`：nums 为整数数组，窗口大小满足 `1 <= k <= len(nums)`。

### 输出与约束

查找返回 target 在当前数组中的 0 起始下标，不存在返回 -1。滑窗返回每个长度为 k 的连续窗口的最大值，按窗口从左到右排列；每次只移动一个位置。

### 示例

```text
search([4,5,6,7,0,1,2], 0) -> 4
search([4,5,6,7,0,1,2], 3) -> -1
max_sliding_window([1,3,-1,-3,5,3,6,7], 3) -> [3,3,5,5,6,7]
```

## 解题思路与参考答案

33 靠的是「旋转以后总有一半是有序的」，二分之前先判断哪一半有序；239 靠单调队列，避免每个窗口都扫一遍 $O(nk)$。两题结构完全不同，但同一轮里常被当成模板题连着问（LeetCode 33 / 239）。

旋转查找时拿 `nums[mid]` 和 `nums[lo]` 比，判断左半是否有序。比如在 `[4,5,6,7,0,1,2]` 里找 0，第一次 mid 落在 7，左半 `4..7` 有序，0 不在这个范围里，就去右半找。目标落在有序那半的闭区间里就收缩到那半，否则去另一半。没有重复元素时每次一定能丢掉一半，时间 $O(\log n)$、空间 $O(1)$。有重复（81）时，`nums[lo]==nums[mid]` 判断不出哪边有序，只能 `lo+=1` 收缩一端，最坏退化成 $O(n)$。

滑窗最大值用双端队列，保持队里下标对应的值递减。新元素 $i$ 进来时，先把队尾比 `a[i]` 小的全部弹出，它们以后不可能再当最大值；队头下标 $\le i-k$ 说明过期了，也弹掉。这时 `a[q.front()]` 就是窗口最大。队里存的是下标，存值的话就没法判断过期。每个下标最多进队、出队各一次，时间 $O(n)$，空间 $O(k)$。堆也能做，但要带下标懒删除，常数更大。

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

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert search([4, 5, 6, 7, 0, 1, 2], 0) == 4` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**33 要测哪些边界？**
没旋转、单元素、目标不存在、旋转点在两端。

**239 呢？**
$k=1$、$k=n$，以及窗口内单调递增或单调递减。

**换成滑窗最小值呢？**
队列改成单调递增就行。
