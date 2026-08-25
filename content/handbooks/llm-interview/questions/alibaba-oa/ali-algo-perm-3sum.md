---
id: ali-algo-perm-3sum
section: alibaba-oa
order: 38
level: A
title: 阿里手撕：全排列和三数之和各自防什么重复？
quick: >-
  46 用 `used` 回溯，交换法注意还原。15 先排序，定 i 后双指针，相同值跳过。排列是生成，三数之和是去重搜索。
tags:
  - Alibaba
  - 回溯
  - 双指针
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 全排列
    url: https://leetcode.cn/problems/permutations/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题 / 考点说明

- 对应：LeetCode 46 / 15

排列是生成：每个位置选一个还没用过的数。三数之和是去重搜索：答案集合里同一三元组只出现一次。46 的输入通常互异；一旦有重复元素就变成 47，必须先排序并跳过同层相同值。

## 思路

46：路径 + `used` 布尔数组。选 `nums[i]` 时标已用，回溯时还原。交换法也可以，但现场要保证换出去的位置还原。有重复（47）先排序，同层 `nums[i]==nums[i-1]` 且前一个没选，则跳过。

15：先排序。枚举 $i$，在 $i+1\ldots n-1$ 上双指针找和为 $-nums[i]$。`nums[i]==nums[i-1]` 跳过；$L/R$ 收答案后也跳过相同值。目标和为 $0$ 时注意用足够位宽做加法。

## 参考代码

```python
from typing import List


def permute(nums: List[int]) -> List[List[int]]:
    n = len(nums)
    used = [False] * n
    path: List[int] = []
    ans: List[List[int]] = []

    def dfs() -> None:
        if len(path) == n:
            ans.append(path[:])
            return
        for i in range(n):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            dfs()
            path.pop()
            used[i] = False

    dfs()
    return ans


def three_sum(nums: List[int]) -> List[List[int]]:
    nums.sort()
    n = len(nums)
    ans: List[List[int]] = []
    for i in range(n):
        if i and nums[i] == nums[i - 1]:
            continue
        if nums[i] > 0:
            break
        left, right = i + 1, n - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s < 0:
                left += 1
            elif s > 0:
                right -= 1
            else:
                ans.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
    return ans


if __name__ == "__main__":
    got = permute([1, 2, 3])
    assert sorted(got) == sorted(
        [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
    )
    assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
    assert three_sum([0, 1, 1]) == []
    assert three_sum([0, 0, 0]) == [[0, 0, 0]]
    print("ok")
```

## 复杂度

- 46：时间 $O(n\cdot n!)$，空间 $O(n)$ 递归栈（不含答案）。
- 15：排序 $O(n\log n)$ 加双指针 $O(n^2)$，空间 $O(1)$ 额外（不含答案）。

## 边界与追问

1. 46：$n=1$、已有序。47 有重复必须同层去重，只靠 `used` 不够。
2. 15：全正 / 全负直接空；`[0,0,0,0]` 只能一组；不要用三重循环再 `set`。
3. 追问四数之和：再套一层枚举，内层仍双指针，注意每层去重。目标和非 $0$ 时把目标传进去。
