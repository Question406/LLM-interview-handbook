---
id: lc-35-search-insert-position
section: binary-search
order: 1
level: S
title: LC 35 · 搜索插入位置
quick: >-
  二分找下界，也就是第一个 $\ge$ `target` 的位置。值存在时它就是下标，不存在时它就是插入位置，全都小于 `target` 时返回 $n$。时间
  $O(\log n)$。
tags:
  - Binary Search
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 35. 搜索插入位置
    url: 'https://leetcode.cn/problems/search-insert-position/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一个严格递增整数数组和目标值 target。如果目标值在数组中，返回它的下标；否则返回把 target 插入数组后仍保持递增顺序时应使用的下标。插入位置可以是数组开头，也可以是数组末尾之后。

### 输入与输出

实现 `searchInsert(nums: List[int], target: int) -> int`。下标从 0 开始，只需返回位置，不需要实际修改数组。要求 O(log n) 时间。

### 约束

- `1 <= len(nums) <= 10^4`。
- 数组元素互不相同且递增，元素与 target 均在 `[-10^4,10^4]` 内。

### 示例

```text
输入：nums = [1,3,5,6], target = 5
输出：2
```

## 解题思路与参考答案

## 题意

升序且互异的 `nums`。找到 `target` 的下标；不存在则返回它应插入的位置，使数组仍有序。

## 思路

这题就是下界二分。我用半开区间，`lo, hi = 0, n`；`nums[mid] < target` 时 `lo = mid + 1`，否则 `hi = mid`。结束时 `lo` 就是第一个不小于 `target` 的下标，值存在就是它的位置，不存在就是插入位置。

拿 `[1,3,5,6]` 找 2。`mid=2` 是 5，不小于 2，`hi=2`；`mid=1` 是 3，`hi=1`；`mid=0` 是 1，小于 2，`lo=1`。返回 1，2 正好插在 1 和 3 之间。

写成闭区间也行，但插入位置在尾部时要单独处理 `hi` 出界。区间约定固定用一种，别混着写。

## 参考代码

```python
from typing import List


def searchInsert(nums: List[int], target: int) -> int:
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo


if __name__ == "__main__":
    assert searchInsert([1, 3, 5, 6], 5) == 2
    assert searchInsert([1, 3, 5, 6], 2) == 1
    assert searchInsert([1, 3, 5, 6], 7) == 4
    assert searchInsert([1, 3, 5, 6], 0) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert searchInsert([1, 3, 5, 6], 5) == 2
assert searchInsert([1, 3, 5, 6], 2) == 1
assert searchInsert([1, 3, 5, 6], 7) == 4
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## Edge Cases

`target` 小于全部时，循环里一直 `hi = mid`，返回 $0$。大于全部时一直 `lo = mid + 1`，返回 $n$，就是尾部插入位。恰好是第一个或最后一个元素时，下界正好落在那个下标，因为第一个 $\ge$ `target` 就是它自己。

## 追问

**有重复怎么办？**
同一套下界在非递减数组上照样正确。本题声明互异，有重复时它返回第一个 $\ge$ `target` 的位置，也就是这个值第一次出现的地方，没有就是应插入处。要求插到这个值最后一次出现之后的话，改用上界。

```python
def searchInsertDup(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

**上界（第一个 $\gt$ `target`）怎么写？**
把比较改成 `nums[mid] \le target` 时 `lo = mid + 1`，否则 `hi = mid`。结束时 `lo` 是第一个大于 `target` 的下标；`target` 最后一次出现在 `lo - 1`，还要再判一下它是不是真的等于 `target`。LC 34 的左右端点就是下界和上界减一，独立卡见 `lc-34-find-first-and-last-position-of-element-in-sorted-array`。

```python
def upper_bound(nums, target):
    lo, hi = 0, len(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```
