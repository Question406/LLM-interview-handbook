---
id: lc-228-summary-ranges
section: intervals
order: 1
level: A
title: LC 228 · 汇总区间
quick: >-
  有序无重复数组上扫连续段。单点写成 `"a"`，一段写成 `"a->b"`。时间
  $O(n)$。
tags:
  - Intervals
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 228. 汇总区间
    url: https://leetcode.cn/problems/summary-ranges/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定升序、无重复的整数数组，把连续区间汇总成字符串列表。长度为 $1$ 的区间写成 `"a"`，否则 `"a->b"`。

## 思路

一次扫描。记下段起点 `start`，只要 `nums[i+1] == nums[i] + 1` 就延伸。断开时：`start == nums[i]` 则输出单点，否则输出 `start->nums[i]`。然后从下一个数开新段。

数组已有序且无重复，不必排序、不必哈希。

## 参考代码

```python
from typing import List


def summaryRanges(nums: List[int]) -> List[str]:
    res = []
    i, n = 0, len(nums)
    while i < n:
        start = nums[i]
        while i + 1 < n and nums[i + 1] == nums[i] + 1:
            i += 1
        if start == nums[i]:
            res.append(str(start))
        else:
            res.append(f"{start}->{nums[i]}")
        i += 1
    return res


if __name__ == "__main__":
    assert summaryRanges([0, 1, 2, 4, 5, 7]) == ["0->2", "4->5", "7"]
    assert summaryRanges([0, 2, 3, 4, 6, 8, 9]) == ["0", "2->4", "6", "8->9"]
    assert summaryRanges([]) == []
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$（不计答案）。每个下标进外层、内层各一次。

## 边界

- 空数组：外层循环不进，返回 `[]`。
- 单元素：内层延伸条件失败，输出 `"a"`。
- 整段连续：外层只跑一轮，得到一条 `"start->end"`。
- 完全不连续：每个数都是单点串。
- 含负数：有序性仍成立，`+1` 判断不受符号影响。

## 追问

- **数组里有重复怎么办？** 题面保证严格递增，相等不会出现。若允许重复，连续相等也应并进同一段：把延伸条件改成 $nums[i+1]\le nums[i]+1$（相等或恰好大 $1$ 都不断开）。输出仍只写两端，中间重复值不会出现在字符串里。也可以先线性去重再跑原算法，额外空间 $O(n)$。时间仍 $O(n)$。面试先问清「重复算一段还是非法输入」。

```python
def summaryRangesDup(nums):
    res, i, n = [], 0, len(nums)
    while i < n:
        start = nums[i]
        while i + 1 < n and nums[i + 1] <= nums[i] + 1:
            i += 1
        res.append(str(start) if start == nums[i] else f"{start}->{nums[i]}")
        i += 1
    return res
```

- **返回闭区间对而不是字符串？** 扫描完全一样，断开时收 `[start, nums[i]]`，单点就是 `[a, a]`。这是「有序数组转区间列表」的标准写法。后续若要合并或插入一段，把这对列表交给 `lc-56-merge-intervals` / `lc-57-insert-interval` 即可。时间 $O(n)$，额外空间只在答案。不要先转字符串再解析回端点。

```python
def summaryRangePairs(nums):
    res, i, n = [], 0, len(nums)
    while i < n:
        start = nums[i]
        while i + 1 < n and nums[i + 1] == nums[i] + 1:
            i += 1
        res.append([start, nums[i]])
        i += 1
    return res
```
