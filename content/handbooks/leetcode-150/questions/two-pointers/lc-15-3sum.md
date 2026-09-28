---
id: lc-15-3sum
section: two-pointers
order: 5
level: S
title: LC 15 · 三数之和
quick: >-
  先排序。固定 `i`，剩余段对撞找 $0-nums[i]$。`i`、`l`、`r` 都跳过重复，保证三元组唯一。时间
  $O(n^2)$，额外空间 $O(1)$。
tags:
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 15. 三数之和
    url: https://leetcode.cn/problems/3sum/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

整数数组 `nums`，找出所有不重复的三元组，使三者之和为 $0$。三元组内顺序不限。

## 思路

排序后枚举 `i`，在它右侧对撞。和小于 $0$ 则 `l` 右移，大于 $0$ 则 `r` 左移，命中就收入并同时收缩。`nums[i] == nums[i-1]` 时跳过；命中后 `l`、`r` 也跳过相同值。`nums[i]` $\gt 0$ 可提前停：后面全正，加不出 $0$。

哈希去重难写且更慢。我会把「跳过重复」讲清楚再写循环。

## 参考代码

```python
from typing import List


def threeSum(nums: List[int]) -> List[List[int]]:
    nums.sort()
    n = len(nums)
    ans: List[List[int]] = []
    for i in range(n - 2):
        if nums[i] > 0:
            break
        if i > 0 and nums[i] == nums[i - 1]:
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


if __name__ == "__main__":
    assert threeSum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
    assert threeSum([0, 1, 1]) == []
    assert threeSum([0, 0, 0]) == [[0, 0, 0]]
    print("ok")
```

## 复杂度

时间 $O(n^2)$，排序 $O(n\log n)$ 被盖住。额外空间 $O(1)$（不计答案与排序开销）。

## 边界

- 不足三个数：答案为空。
- 全正 / 全负加不出 $0$；`[0,0,0]` 要收一组。
- 大量重复：`i`、`l`、`r` 都跳过，否则会爆出重复三元组。

## 追问

- **最接近 `target` 的三数和（LC 16）？** 同样排序 + 枚举 `i` + 对撞。不收集全部三元组，只维护一个 `best`：每次用当前和与 `target` 的绝对差去更新。和偏小 `l` 右移，偏大 `r` 左移，相等直接返回 `target`。时间 $O(n^2)$，空间 $O(1)$。不必跳过重复也能过，因为只关心值；跳过可以少几次循环。这块容易栽：用「是否更接近」比较时写成 `s - target` 没加绝对值，或初始化 `best` 用 $0$ 而不是前三个数的和。

```python
def threeSumClosest(nums, target):
    nums.sort()
    best = nums[0] + nums[1] + nums[2]
    n = len(nums)
    for i in range(n - 2):
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if abs(s - target) < abs(best - target):
                best = s
            if s < target:
                l += 1
            elif s > target:
                r -= 1
            else:
                return s
    return best
```

- **四数之和（LC 18）？** 再套一层：排序后枚举 `i`、`j`，在 $j$ 右侧对撞找 `target - nums[i] - nums[j]`。`i`、`j`、`l`、`r` 都要跳过与前一个相同的值。时间 $O(n^3)$，空间 $O(1)$。可用提前剪枝：当前最小四数之和已经 $\gt$ `target` 就 `break`，最大四数之和 $\lt$ `target` 就 `continue`。别写成四重循环 $O(n^4)$。$k$ 数之和就是外层 $k-2$ 重枚举 + 最内层对撞，复杂度 $O(n^{k-1})$。

```python
def fourSum(nums, target):
    nums.sort()
    n, ans = len(nums), []
    for i in range(n - 3):
        if i and nums[i] == nums[i - 1]:
            continue
        for j in range(i + 1, n - 2):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            l, r = j + 1, n - 1
            while l < r:
                s = nums[i] + nums[j] + nums[l] + nums[r]
                if s < target:
                    l += 1
                elif s > target:
                    r -= 1
                else:
                    ans.append([nums[i], nums[j], nums[l], nums[r]])
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
                    while l < r and nums[r] == nums[r + 1]:
                        r -= 1
    return ans
```
