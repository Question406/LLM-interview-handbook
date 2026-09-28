---
id: lc-724-find-pivot-index
section: prefix-sum
order: 2
level: S
title: LC 724 · 寻找数组的中心下标
quick: >-
  先求总和 `total`，从左扫时维护左侧和 `left`；右侧和就是 `total - left - nums[i]`，相等即返回最左的 $i$。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Prefix Sum
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 724. Find Pivot Index
    url: https://leetcode.com/problems/find-pivot-index/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

中心下标 $i$ 满足：严格在它左边的元素之和等于严格在它右边的元素之和，`nums[i]` 本身不算。左端 $i=0$ 时左侧和为 $0$，右端同理。返回最靠左的中心下标，没有返回 $-1$。$n \le 10^4$，元素可正可负。

## 思路

右侧和可以由总和推出：$\text{right} = \text{total} - \text{left} - nums[i]$。所以先扫一遍求 `total`，再从左扫，每个位置先判 `left == total - left - nums[i]`，再把 `nums[i]` 加进 `left`。先判后加，保证 `left` 不含自己。

从左往右第一个命中的就是最左答案。元素有负数，左右和不单调，别想着用双指针往中间逼。对每个 $i$ 分别求左右和是 $O(n^2)$。

## 参考代码

```python
from typing import List


def pivotIndex(nums: List[int]) -> int:
    total = sum(nums)
    left = 0
    for i, x in enumerate(nums):
        if left == total - left - x:
            return i
        left += x
    return -1


if __name__ == "__main__":
    assert pivotIndex([1, 7, 3, 6, 5, 6]) == 3
    assert pivotIndex([1, 2, 3]) == -1
    assert pivotIndex([2, 1, -1]) == 0
    assert pivotIndex([0]) == 0
    assert pivotIndex([-1, -1, 0, 1, 1, 0]) == 5
    assert pivotIndex([0, 0, 0]) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，两遍扫描。额外空间 $O(1)$。

## 边界

- 答案在最左端：`[2, 1, -1]` 右侧和为 $0$，左侧空和也是 $0$，返回 $0$。
- 答案在最右端：右侧空和为 $0$，公式里 `total - left - x` 自然给出 $0$。
- 多个中心下标，如全 $0$：返回第一个。
- 负数导致左右和不单调：只能线性扫，不能二分或双指针。

## 追问

- **不排除 `nums[i]`，改成把数组切成两段和相等（切点在两元素之间）？** 条件变成 `left == total - left`，即 `2 * left == total`，其中 `left` 包含到切点为止的元素。`total` 为奇数可直接判无解。时间 $O(n)$，额外空间 $O(1)$。

```python
def splitPoint(nums):
    total = sum(nums)
    left = 0
    for i in range(len(nums) - 1):
        left += nums[i]
        if 2 * left == total:
            return i + 1
    return -1
```

- **要多次查询任意区间的和？** 开前缀和数组 `pre`，`pre[0] = 0`、`pre[i+1] = pre[i] + nums[i]`，区间 `[l, r]` 的和是 `pre[r+1] - pre[l]`。预处理 $O(n)$，单次查询 $O(1)$。本题只是其中一个特例，用滚动变量省掉了数组。
