---
id: lc-153-find-minimum-in-rotated-sorted-array
section: binary-search
order: 6
level: A
title: LC 153 · 寻找旋转排序数组中的最小值
quick: "拿 `nums[mid]` 和右端比，`nums[mid] > nums[hi]` 说明最小值在右半，否则就是 `mid` 本身或在左边。缩到 `lo == hi` 就是答案。数组无重复，时间 $O(\\log n)$。"
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 153. 寻找旋转排序数组中的最小值
    url: https://leetcode.cn/problems/find-minimum-in-rotated-sorted-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

原本严格递增的整数数组经过若干次旋转后成为 nums。一次旋转把最后一个元素移到数组最前面，例如 `[1,2,3]` 旋转一次变成 `[3,1,2]`。请返回旋转后数组中的最小值。

### 输入与输出

实现 `findMin(nums: List[int]) -> int`，返回最小元素的值，而不是它的下标。要求时间复杂度 O(log n)。

### 约束

- `1 <= len(nums) <= 5000`，元素范围为 `[-5000,5000]`。
- 元素互不相同，输入保证来自一个严格递增数组的 1 到 n 次旋转；旋转 n 次可以恢复原数组。

### 示例

```text
输入：nums = [3,4,5,1,2]
输出：1
```

## 解题思路与参考答案

## 题意

升序互异数组旋转后，找最小值。要求 $O(\log n)$。

## 思路

最小值就是旋转点，我会二分，每次拿 `nums[mid]` 和右端 `nums[hi]` 比。`nums[mid] > nums[hi]` 说明断点在 `mid` 右边，`lo = mid + 1`；否则 `mid` 可能就是最小值，`hi = mid`。

拿 `[4,5,6,7,0,1,2]` 走一遍。`mid=3` 是 7，大于右端的 2，最小值在右边，`lo=4`；`mid=5` 是 1，不大于 2，`hi=5`；`mid=4` 是 0，不大于 1，`hi=4`。`lo == hi == 4`，答案是 0。

和左端比不好用，未旋转时左端一直是最小，没法据此丢掉哪一半。有重复是 LC 154，`nums[mid] == nums[hi]` 时只能 `hi -= 1`。

## 参考代码

```python
from typing import List


def findMin(nums: List[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]


if __name__ == "__main__":
    assert findMin([3, 4, 5, 1, 2]) == 1
    assert findMin([4, 5, 6, 7, 0, 1, 2]) == 0
    assert findMin([11, 13, 15, 17]) == 11
    assert findMin([1]) == 1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert findMin([3, 4, 5, 1, 2]) == 1
assert findMin([4, 5, 6, 7, 0, 1, 2]) == 0
assert findMin([11, 13, 15, 17]) == 11
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## 边界

未旋转（已经升序）时，`nums[mid]` 一直 $\le$ `nums[hi]`，`hi` 收到 `0`，答案是第一个元素。最小值在末尾的情况形如 `[2,3,4,5,1]`，`mid` 落在左半时 `nums[mid] \gt nums[hi]`，`lo` 会一路推到末尾。$n=1$ 时 `lo == hi`，循环不进，直接返回唯一的元素。

## 追问

**有重复（LC 154）怎么办？**
相等时只能 `hi -= 1`，最坏退化成 $O(n)$。无重复时 `nums[mid] == nums[hi]` 只可能是 `mid == hi`；有重复后，`[1,1,1]`、`[3,1,3]`、`[1,3,1]` 这三种情况一次比较判断不了断点在哪边。`nums[mid] \gt nums[hi]` 仍然把 `lo` 推到右半，`nums[mid] \lt nums[hi]` 仍然把 `hi` 收到 `mid`；相等时丢掉右端这个副本是安全的，它确定不是唯一的最小值。平均仍很快，全相等时最坏 $O(n)$，没法再保证 $\log$。独立卡见 `lc-154`。

```python
def findMinDup(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        elif nums[mid] < nums[hi]:
            hi = mid
        else:
            hi -= 1
    return nums[lo]
```

**同时要找目标（LC 33）呢？**
找最小值只需跟右端比、丢掉确定更大的半段。要找 `target` 时，先用 `nums[lo] \le nums[mid]` 判断哪一半有序，再看 `target` 是否落在这一半的值域里，落入就缩进有序半，否则丢掉它。还是一次二分，$O(\log n)$。独立卡见 `lc-33-search-in-rotated-sorted-array`。

```python
def searchRotated(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[lo] <= nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```
