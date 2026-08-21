---
id: lc-167-two-sum-ii-input-array-is-sorted
section: two-pointers
order: 3
level: S
title: LC 167 · 两数之和 II - 输入有序数组
quick: >-
  有序数组对撞：和小了左移，大了右移。命中后返回 $1$-index。时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 167. 两数之和 II - 输入有序数组
    url: https://leetcode.cn/problems/two-sum-ii-input-array-is-sorted/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

非递减数组 `numbers`，找两个下标使对应值之和等于 `target`。恰好一组解，按下标从 $1$ 开始返回。

## 思路

`l`、`r` 放在两端。和等于 `target` 就返回 `[l+1, r+1]`；和偏小则 `l` 右移（要更大），偏大则 `r` 左移。有序保证不会漏解。

哈希也能做，但题目要求常数额外空间。面试先点明「有序才能对撞」。

## 参考代码

```python
from typing import List


def twoSum(numbers: List[int], target: int) -> List[int]:
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target:
            return [l + 1, r + 1]
        if s < target:
            l += 1
        else:
            r -= 1
    return []


if __name__ == "__main__":
    assert twoSum([2, 7, 11, 15], 9) == [1, 2]
    assert twoSum([2, 3, 4], 6) == [1, 3]
    assert twoSum([-1, 0], -1) == [1, 2]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每步丢掉一端，互斥地收缩。

## 边界

- 负数加正数：对撞照样成立，有序不要求全正。
- 两个相同值相加：`l`、`r` 停在两个不同位置即可。
- 答案在最两端：第一次比较就命中。

## 追问

- **数组无序（LC 1）？** 对撞依赖有序，无序会漏解。改一遍哈希：扫到 $x$ 时查 $target-x$ 是否已出现，先查再写下标。时间 $O(n)$，额外空间升到 $O(n)$。本题要求常数空间且返回 $1$-index，有序才对撞。独立卡见 `lc-1-two-sum`。不要先排序再对撞再映射回原下标，排序已经 $O(n\log n)$，还要处理重复值。

```python
def twoSum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []
```

- **三数之和（LC 15）？** 无序数组找不重复三元组使和为 $0$。先排序，枚举 `i`，右侧对撞找 $-nums[i]$。`i`、`l`、`r` 跳过重复值；$nums[i] \gt 0$ 提前停。时间 $O(n^2)$，空间 $O(1)$。不要对每个 `i` 再套一遍本题的两数之和哈希，去重会很难写。独立卡见 `lc-15-3sum`。

```python
def threeSum(nums):
    nums.sort()
    n, ans = len(nums), []
    for i in range(n - 2):
        if nums[i] > 0:
            break
        if i and nums[i] == nums[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                ans.append([nums[i], nums[l], nums[r]])
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:
                    l += 1
                while l < r and nums[r] == nums[r + 1]:
                    r -= 1
    return ans
```
