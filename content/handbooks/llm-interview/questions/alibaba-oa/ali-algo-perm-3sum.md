---
id: ali-algo-perm-3sum
section: alibaba-oa
order: 38
level: A
title: 阿里手撕：全排列和三数之和各自防什么重复？
quick: >-
  全排列（46）要生成所有顺序，用 `used`
  标记当前路径已用的元素，回溯时还原；用交换法的话换出去的位置要换回来。三数之和（15）要每个三元组只出现一次，先排序，固定一个数后双指针找另外两个，固定数和左右指针都跳过重复值。
tags:
  - Alibaba
  - 回溯
  - 双指针
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 全排列
    url: 'https://leetcode.cn/problems/permutations/'
    type: primary
  - title: 2026 校招高频题总览
    url: 'https://www.cnblogs.com/autodriver/p/19829365'
    type: secondary
---

## 题目描述

实现两个独立函数，分别处理排列枚举与三数求和。输入和返回值均使用 Python 列表。

### 接口与约束

- `permute(nums)`：`nums` 为互不相同的整数，返回使用每个输入元素恰好一次形成的所有排列。每个排列的长度等于输入长度；结果列表的顺序不限，但不能遗漏或重复。
- `three_sum(nums)`：输入整数列表，找出所有由三个不同下标组成、元素和为 0 的三元组。输入允许重复值，输出按值去重；同一组三个值只能出现一次，不同下标但相同值不算新答案。允许调整输入数组的顺序。结果中三元组及三元组列表的排列顺序不限。

### 示例

```text
permute([1,2]) -> [[1,2],[2,1]]（顺序不限）
three_sum([-1,0,1,2,-1,-4]) -> [[-1,-1,2],[-1,0,1]]
three_sum([0,0,0,0])       -> [[0,0,0]]
three_sum([0,1,1])         -> []
```

这是按相关公开算法考点整理的练习约定，不包含带重复元素的全排列变体。

## 解题思路与参考答案

两道题防的东西不一样。全排列要把所有顺序都生成出来，防的是同一个元素在一条路径里用两次；三数之和要求答案集合里每个三元组只出现一次，防的是重复的三元组。对应 LeetCode 46 和 15。

46 用一条路径加一个 `used` 布尔数组：选 `nums[i]` 时标成已用，递归回来再还原。交换法也可以，但现场要保证换出去的位置换回来。46 的输入通常互不相同；有重复元素就变成了 47，只靠 `used` 不够，要先排序，同一层里 `nums[i]==nums[i-1]` 且前一个没选时跳过。

15 先排序，然后枚举 $i$，在 $i+1\ldots n-1$ 上用双指针找和为 $-nums[i]$ 的两个数。`nums[i]==nums[i-1]` 就跳过；左右指针收到一个答案以后，也要跳过相同的值。比如 `[0,0,0,0]` 只能出一组。别用三重循环再丢进 `set` 去重。目标和为 $0$ 时，加法注意用足够的位宽。

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

46 时间 $O(n\cdot n!)$，递归栈 $O(n)$（不含答案）。15 是排序 $O(n\log n)$ 加双指针 $O(n^2)$，额外空间 $O(1)$（不含答案）。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

先从题中测试代码中的第一个场景开始，保留它的输入准备、调用和断言，再逐步补其他场景。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**46 要覆盖哪些 edge cases？**
$n=1$，以及输入已经有序的情况。

**三数之和什么时候直接返回空？**
全正或全负的时候。代码里固定的数已经大于 0 就直接 `break`。

**四数之和怎么写？**
再套一层枚举，内层还是双指针，每一层都要去重。目标和不是 $0$ 时，把目标作为参数传进去。
