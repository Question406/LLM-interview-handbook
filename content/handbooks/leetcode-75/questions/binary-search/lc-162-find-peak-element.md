---
id: lc-162-find-peak-element
section: binary-search
order: 3
level: S
title: LC 162 · 寻找峰值
quick: >-
  比较 `mid` 和 `mid+1` 做二分，往更大的一侧走，那一侧一定有峰（两端外视为 $-\infty$）。时间 $O(\log n)$，额外空间 $O(1)$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 162. Find Peak Element
    url: https://leetcode.com/problems/find-peak-element/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定相邻元素互不相等的整数数组，若某个元素严格大于它左右相邻元素，就称它为峰值。数组两端之外的数视为负无穷，因此端点也可能成为峰值。返回任意一个峰值的位置。

### 输入与输出

实现 `findPeakElement(nums) -> int`，返回从 0 开始的下标。数组可能有多个峰值，此时任意一个满足条件的下标都有效；不要求返回最高的峰值。

### 约束与约定

- `1 <= len(nums) <= 1000`。
- 元素在 32 位有符号整数范围内。
- 任意合法相邻位置都满足 `nums[i] != nums[i+1]`；要求 `O(log n)` 时间。

### 示例

```text
输入：nums = [1,2,3,1]
输出：2
```

示例中 nums[2]=3 大于左右的 2 和 1，所以返回下标 2。

[官方原题与完整题面](https://leetcode.com/problems/find-peak-element/description/)。

## 解题思路与参考答案

## 题意

`nums[i]` 是峰值当它严格大于左右邻居。数组两端外侧看成负无穷，相邻元素保证不同。返回任一峰值下标，要求 $O(\log n)$。

## 思路

题目要 $O(\log n)$，我会二分，依据是往高处走一定能碰到峰。`nums[mid]` 小于 `nums[mid+1]` 说明右侧在上升：要么一直升到尽头，尽头就是峰；要么中途下降，下降前就是峰。所以往右收，`lo = mid + 1`。反过来就往左收，`mid` 自己可能就是峰，所以 `hi = mid`。

拿 `[1, 2, 3, 1]` 走一遍：`lo=0, hi=3`，`mid=1`，2 小于 3，`lo=2`；`mid=2`，3 大于 1，`hi=2`；区间缩成一个点，返回 2。

区间 $[lo, hi]$ 始终满足「里面一定有峰」，收缩到一个点就是答案。相邻元素保证不同，所以不会卡在平台上。线性扫找第一个下降点也能做，但那是 $O(n)$，不符合要求。

## 参考代码

```python
from typing import List


def findPeakElement(nums: List[int]) -> int:
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo


def isPeak(nums: List[int], i: int) -> bool:
    left = nums[i - 1] if i > 0 else float("-inf")
    right = nums[i + 1] if i + 1 < len(nums) else float("-inf")
    return nums[i] > left and nums[i] > right


if __name__ == "__main__":
    assert findPeakElement([1, 2, 3, 1]) == 2
    assert findPeakElement([1, 2, 1, 3, 5, 6, 4]) in (1, 5)
    assert findPeakElement([1]) == 0
    assert findPeakElement([1, 2, 3, 4]) == 3
    assert findPeakElement([4, 3, 2, 1]) == 0
    for nums in ([3, 1, 2], [1, 3, 2, 4, 1], [2, 1]):
        assert isPeak(nums, findPeakElement(nums))
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert findPeakElement([1, 2, 3, 1]) == 2
assert findPeakElement([1, 2, 1, 3, 5, 6, 4]) in (1, 5)
assert findPeakElement([1]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## 边界

- $n=1$ 时两端外侧都是 $-\infty$，唯一元素就是峰，循环不进，返回 $0$。
- 单调升时每次都往右收，`lo` 推到末尾，峰在最后一个。
- 单调降时每次往左收，`hi = mid` 一路收到下标 $0$。
- 有多个峰时，算法保证停在其中一个，不一定是全局最大。

## 追问

**二维峰值（LC 1901）怎么做？**
对列二分。$m\times n$ 矩阵里，峰定义为严格大于四邻，边上缺的方向视为 $-\infty$。取中列 `mid`，找到该列最大值所在行 `row`。它比左右邻都大就是峰，上下邻不会更大，因为它是列最大；左邻更大，峰必在左半，右邻更大就去右半。时间 $O(m\log n)$。

```python
def findPeakGrid(mat):
    m, n = len(mat), len(mat[0])
    lo, hi = 0, n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        row = max(range(m), key=lambda r: mat[r][mid])
        left = mat[row][mid - 1] if mid else float("-inf")
        right = mat[row][mid + 1] if mid + 1 < n else float("-inf")
        if mat[row][mid] > left and mat[row][mid] > right:
            return [row, mid]
        if left > mat[row][mid]:
            hi = mid - 1
        else:
            lo = mid + 1
```

**为什么比 `mid+1`，不比 `mid-1`？**
因为循环条件是 `lo < hi` 且 `mid` 向下取整，`mid+1` 一定不越界。比 `mid-1` 就要改成向上取整，否则 `mid = lo` 时会越界或死循环。

**允许相邻相等，还能 $O(\log n)$ 吗？**
不能保证。全相等数组里根本没有严格峰；像 `[1,1,1,2,1,1,1]` 这样的输入，二分看到的中点和邻居都相等，判断不了峰在哪一侧，最坏只能线性扫。
