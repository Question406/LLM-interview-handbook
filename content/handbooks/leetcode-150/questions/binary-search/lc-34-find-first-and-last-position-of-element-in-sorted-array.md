---
id: lc-34-find-first-and-last-position-of-element-in-sorted-array
section: binary-search
order: 5
level: A
title: LC 34 · 在排序数组中查找元素的第一个和最后一个位置
quick: >-
  两次二分。下界是第一个 $\ge$ `target` 的位置，上界是第一个 $\gt$ `target` 的位置，最后一次出现是上界减一；下界越界或值不等于
  `target` 就返回 $[-1,-1]$。时间 $O(\log n)$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 34. 在排序数组中查找元素的第一个和最后一个位置
    url: >-
      https://leetcode.cn/problems/find-first-and-last-position-of-element-in-sorted-array/
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定非递减整数数组 `nums` 和整数 `target`，找出 target 在数组中出现的最左下标和最右下标。目标可能连续出现多次，也可能完全不存在；空数组属于合法输入。

### 输入与输出

实现 `searchRange(nums, target) -> List[int]`，返回 `[first, last]`。下标从 0 开始；目标不存在时返回 `[-1, -1]`。要求运行时间为 O(log n)。

### 约束

- `0 <= len(nums) <= 10^5`，数组保证非递减。
- `-10^9 <= nums[i] <= 10^9`。
- `-10^9 <= target <= 10^9`。

### 示例

```text
输入：nums = [5,7,7,8,8,10], target = 8
输出：[3,4]
```

[LeetCode 原题](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/description/)

## 解题思路与参考答案

## 题意

非递减数组，返回 `target` 第一次和最后一次出现的下标。不存在返回 $[-1,-1]$。要求 $O(\log n)$。

## 思路

我会写两次二分，分别寻找 left / right bounds。下界是第一个 $\ge target$ 的位置，如果它越界或者值不是 `target`，说明数组里没有；上界是第一个 $> target$ 的位置，最后一次出现就是它减一。两次二分的比较符只差一个等号，代码里用一个 `upper` 参数合成了一个函数。

拿 `[5,7,7,8,8,10]` 找 8。第一个不小于 8 的是下标 3，第一个大于 8 的是下标 5（值 10），所以答案是 `[3,4]`。找 6 时下界落在下标 1，值是 7，不等于 6，返回 $[-1,-1]$。

找到一个再左右线性扩也能写，但重复很多时会退化成 $O(n)$。

## 参考代码

```python
from typing import List


def searchRange(nums: List[int], target: int) -> List[int]:
    def bound(upper: bool) -> int:
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < target or (upper and nums[mid] == target):
                lo = mid + 1
            else:
                hi = mid
        return lo

    left = bound(False)
    if left == len(nums) or nums[left] != target:
        return [-1, -1]
    return [left, bound(True) - 1]


if __name__ == "__main__":
    assert searchRange([5, 7, 7, 8, 8, 10], 8) == [3, 4]
    assert searchRange([5, 7, 7, 8, 8, 10], 6) == [-1, -1]
    assert searchRange([], 0) == [-1, -1]
    assert searchRange([1], 1) == [0, 0]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert searchRange([5, 7, 7, 8, 8, 10], 8) == [3, 4]
assert searchRange([5, 7, 7, 8, 8, 10], 6) == [-1, -1]
assert searchRange([], 0) == [-1, -1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## Edge Cases

空数组时 `bound` 返回 $0$，$0 == n$，直接 $[-1,-1]$。只出现一次时，下界和上界减一重合。整段都是 `target` 时，下界 $0$、上界 $n$，答案 $[0, n-1]$。`target` 比全部都小时下界是 $0$ 但值不匹配，比全部都大时下界是 $n$，都返回 $[-1,-1]$。

## 追问

**只数出现次数呢？**
上界减下界就是次数，也就是「第一个 $\gt$ `target`」减「第一个 $\ge$ `target`」。没有这个值时两者相等，都指向插入位，差为 $0$。同样别找到一个再左右线性扩，重复多时会退化成 $O(n)$。下界的写法和 LC 35 一样。

```python
def count(nums, target):
    def bound(upper):
        lo, hi = 0, len(nums)
        while lo < hi:
            mid = (lo + hi) // 2
            if nums[mid] < target or (upper and nums[mid] == target):
                lo = mid + 1
            else:
                hi = mid
        return lo

    return bound(True) - bound(False)
```

**旋转数组里找区间怎么做？**
先找最小值，把数组拆成两段有序的，再对每段做本题的下界和上界。无重复时目标最多出现一次，退化成 LC 33。有重复时，同一个值可能在旋转点被劈成两段，一段在数组头、一段在尾，例如 `[2,2,3,4,2,2]` 里 $2$ 的下标不连续。做法是先用 LC 154 的方式找最小值下标 `p`（相等时 `hi -= 1`），把数组拆成有序段 `[0, p)` 和 `[p, n)`，分别求下界和上界。只有一段命中，就返回这一段的 `[L, R]`；两段都命中时，物理下标构不成一个闭区间，应该把头段和尾段都返回。合成「从右段左端到左段右端」会把中间不是 `target` 的元素也包进去。因为有重复，找 `p` 最坏是 $O(n)$。

```python
def searchRangeRotated(nums, target):
    n = len(nums)
    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        elif nums[mid] < nums[hi]:
            hi = mid
        else:
            hi -= 1
    p = lo

    def bound(l, r, upper):
        while l < r:
            mid = (l + r) // 2
            if nums[mid] < target or (upper and nums[mid] == target):
                l = mid + 1
            else:
                r = mid
        return l

    def seg(l, r):
        a = bound(l, r, False)
        if a == r or nums[a] != target:
            return None
        return [a, bound(l, r, True) - 1]

    left, right = seg(0, p), seg(p, n)
    if left and right:
        return [left, right]
    return left or right or [-1, -1]
```
