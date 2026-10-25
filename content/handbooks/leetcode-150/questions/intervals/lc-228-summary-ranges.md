---
id: lc-228-summary-ranges
section: intervals
order: 1
level: A
title: LC 228 · 汇总区间
quick: >-
  在有序无重复的数组上扫一遍，找出每一段连续的数。单点写成 `"a"`，一段写成 `"a->b"`，时间 $O(n)$。
tags:
  - Intervals
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 228. 汇总区间
    url: https://leetcode.cn/problems/summary-ranges/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定已经递增排序、没有重复值的整数数组，把所有元素用尽可能少的连续整数区间表示。每个区间内的整数都必须出现在输入中，不同区间不能重叠，输出按区间起点递增。

### 输入与输出

实现 `summaryRanges(nums) -> list[str]`。单个数 a 写成字符串 "a"；包含多个连续数的区间从 a 到 b 写成 "a->b"。空数组返回空列表。

### 约束与约定

- `0 <= len(nums) <= 20`。
- 数值属于 32 位有符号整数范围，输入已升序排列且没有重复。

### 示例

```text
输入：nums = [0,1,2,4,5,7]
输出：["0->2","4->5","7"]
```

示例可分成 [0,1,2]、[4,5] 和 [7] 三段。

[官方原题与完整题面](https://leetcode.com/problems/summary-ranges/description/)。

## 解题思路与参考答案

## 题意

给定升序、无重复的整数数组，把连续区间汇总成字符串列表。长度为 $1$ 的区间写成 `"a"`，否则写成 `"a->b"`。

## 思路

一次扫描就够。数组已经有序且无重复，不用排序，也不用哈希。我记下当前段的起点 `start`，只要 `nums[i+1] == nums[i] + 1` 就继续延伸。断开时，`start == nums[i]` 就输出单点，否则输出 `start->nums[i]`，然后从下一个数开新段。

拿 `[0,1,2,4,5,7]` 来说：从 0 延伸到 2，碰到 4 断开，输出 `"0->2"`；从 4 延伸到 5，输出 `"4->5"`；7 自己一段，输出 `"7"`。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert summaryRanges([0, 1, 2, 4, 5, 7]) == ["0->2", "4->5", "7"]
assert summaryRanges([0, 2, 3, 4, 6, 8, 9]) == ["0", "2->4", "6", "8->9"]
assert summaryRanges([]) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$（不计答案）。每个下标进外层、内层各一次。

## 边界

空数组时外层循环不进，返回 `[]`。单个元素时延伸条件不成立，输出 `"a"`。整段连续时外层只跑一轮，得到一条 `"start->end"`。完全不连续时每个数都是单点串。有负数也没关系，数组仍然有序，`+1` 的判断不受符号影响。

## 追问

**数组里有重复怎么办？**
先问清楚重复算一段还是非法输入。题面保证严格递增，相等不会出现。如果允许重复，连续相等也应该并进同一段，把延伸条件改成 $nums[i+1]\le nums[i]+1$，相等或者恰好大 $1$ 都不断开。输出仍然只写两端，中间的重复值不会出现在字符串里。也可以先线性去重再跑原算法，额外空间 $O(n)$。时间仍是 $O(n)$。

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

**要返回闭区间对，不要字符串呢？**
扫描完全一样，断开时收 `[start, nums[i]]`，单点就是 `[a, a]`。这是「有序数组转区间列表」的标准写法。之后要合并或插入一段，就把这组区间交给 `lc-56-merge-intervals` / `lc-57-insert-interval`。时间 $O(n)$，额外空间只在答案上。别先转成字符串再解析回端点。

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
