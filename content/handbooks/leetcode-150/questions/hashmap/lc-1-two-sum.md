---
id: lc-1-two-sum
section: hashmap
order: 6
level: S
title: LC 1 · 两数之和
quick: >-
  一边扫一边把「值 $\to$ 下标」放进哈希。当前数的 complement $= target - x$ 已出现就返回答案。时间
  $O(n)$。
tags:
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 1. 两数之和
    url: https://leetcode.cn/problems/two-sum/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

在数组里找两个不同下标 $i$、$j$，使 `nums[i] + nums[j] = target`。保证恰好一组解。返回下标，不是值。

## 思路

一遍哈希：扫到 $x$ 时查 $target - x$ 是否已在表里。在则返回「旧下标、当前下标」；否则把 $x$ 的下标写入。必须先查再写，避免同一个元素用两次（`[3,3]`、$target=6$ 仍合法，因为是两个位置）。

排序双指针也能找值，但会打乱下标，还要再映射回去；白板我默认讲哈希。

## 参考代码

```python
from typing import List


def twoSum(nums: List[int], target: int) -> List[int]:
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []


if __name__ == "__main__":
    assert twoSum([2, 7, 11, 15], 9) == [0, 1]
    assert twoSum([3, 2, 4], 6) == [1, 2]
    assert twoSum([3, 3], 6) == [0, 1]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。每个元素入表一次。

## 边界

- 负数、零都合法，哈希只比「值是否出现过」，不依赖正负。
- 两个相同值如 `[3,3]`、$target=6$：必须先查再写，两个不同下标都能配对。
- 答案可能在开头或结尾，一遍从左扫到右都能覆盖。

## 追问

- **有多解、要所有无重复对？** 本题保证恰好一组，返回任一即可。若改成「所有和为 `target` 的无重复值对」，先排序再左右对撞：和小了 `l` 右移，大了 `r` 左移，命中后两边同时跳过相同值。时间 $O(n\log n)$，额外空间 $O(1)$（不计答案）。易错点是命中后忘记去重，会把 `[1,1,1,2]`、$target=3$ 打成多组相同对。下标版不能排序，还是哈希；值对版才排序。

```python
def twoSumAllPairs(nums, target):
    nums = sorted(nums)
    l, r = 0, len(nums) - 1
    ans = []
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            ans.append([nums[l], nums[r]])
            l += 1
            r -= 1
            while l < r and nums[l] == nums[l - 1]:
                l += 1
            while l < r and nums[r] == nums[r + 1]:
                r -= 1
        elif s < target:
            l += 1
        else:
            r -= 1
    return ans
```

- **三数之和（LC 15）？** 不要三重哈希，难去重且更慢。排序后枚举 `i`，在右侧对撞找 $-nums[i]$：和偏小 `l` 右移，偏大 `r` 左移。`i`、`l`、`r` 都要跳过与前一个相同的值，三元组才唯一。$nums[i] \gt 0$ 可提前停，后面全正加不出 $0$。时间 $O(n^2)$，额外空间 $O(1)$。独立卡见 `lc-15-3sum`。

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
