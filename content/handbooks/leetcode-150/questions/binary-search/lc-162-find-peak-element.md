---
id: lc-162-find-peak-element
section: binary-search
order: 3
level: A
title: LC 162 · 寻找峰值
quick: "二分，比较 `mid` 和 `mid+1`，往更大的那一侧走，那边一定有峰，因为两端外侧都视为 $-\\infty$。时间 $O(\\log n)$。"
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 162. 寻找峰值
    url: https://leetcode.cn/problems/find-peak-element/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定整数数组 nums。某个位置的值严格大于它左右相邻位置的值时，该位置是峰值。为了统一处理两端，把数组外的 `nums[-1]` 和 `nums[n]` 在数学意义上视为负无穷，并不是读取 Python 的负下标。找出任意一个峰值。

### 接口与输出

实现 `findPeakElement(nums: List[int]) -> int`，返回一个峰值的 0-based 下标。数组可能有多个峰值，返回其中任何一个都合法；要求时间复杂度为 `O(log n)`。

### 合法输入与约束

`1 <= len(nums) <= 1000`，元素是 32 位有符号整数，并且每对相邻元素都不相等。长度为 1 时，唯一位置就是峰值。

### 示例

```text
输入：nums = [1,2,3,1]
输出：2
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/find-peak-element/description/)。

## 解题思路与参考答案

## 题意

`nums[i]` 是峰值当它严格大于邻居。数组两端外侧看成负无穷。返回任一峰值下标，要求 $O(\log n)$。

## 思路

我会二分，每次比较 `nums[mid]` 和 `nums[mid+1]`。`nums[mid] < nums[mid+1]` 说明右边在上升，要么一直升到尽头，尽头就是峰；要么中途下降，下降前那个就是峰。所以往右收，`lo = mid + 1`。反过来就往左收，`mid` 自己可能就是峰，所以 `hi = mid`。

拿 `[1,2,3,1]` 走一遍。`mid=1` 是 2，小于右边的 3，往右，`lo=2`；`mid=2` 是 3，大于右边的 1，`hi=2`。停在下标 2。

相邻元素保证不同，不会卡在平台上。线性扫一遍也能做，但达不到时间要求。

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


if __name__ == "__main__":
    assert findPeakElement([1, 2, 3, 1]) == 2
    assert findPeakElement([1, 2, 1, 3, 5, 6, 4]) in (1, 5)
    assert findPeakElement([1]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

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

$n=1$ 时两端外侧是 $-\infty$，唯一的元素就是峰，循环不进，返回 $0$。单调升时每次都是 `nums[mid] \lt nums[mid+1]`，`lo` 推到末尾，峰是最后一个。单调降时每次往左收，`hi = mid` 收到下标 $0$。有多个峰时，算法保证停在其中一个，不一定是全局最大。

## 追问

**二维峰值（LC 1901）怎么做？**
对列二分，时间 $O(m\log n)$。$m\times n$ 矩阵里，峰的定义是严格大于四个邻居，边上缺的方向视为 $-\infty$。取中间列 `mid`，找到这一列最大值所在的行 `row`。它比左邻右邻都大，就是峰；左邻更大，峰一定在左半，因为从这一列往左是上升的，和一维同理；右邻更大就去右半。列方向二分 $\log n$ 步，每步扫一列 $O(m)$。对行二分则是 $O(n\log m)$。整张表直接套一维峰值是行不通的，相邻列之间没有「整列单调」的保证。

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

**允许相邻相等呢？**
那就没法保证 $\log$ 了，最坏退化成 $O(n)$。本题保证相邻不同，所以 `mid` 和 `mid+1` 比一次就知道是升还是降。有平台时 `nums[mid] == nums[mid+1]`，判断不了峰在哪边，只能沿着相等段扩到边界，再看外侧是升还是降。外侧上升就往那边走，两侧都下降，平台本身就是峰。整段都相等就是最坏情况。

```python
def findPeakWithPlateau(nums):
    n, lo, hi = len(nums), 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < nums[mid + 1]:
            lo = mid + 1
        elif nums[mid] > nums[mid + 1]:
            hi = mid
        else:
            r = mid
            while r + 1 < n and nums[r] == nums[r + 1]:
                r += 1
            if r + 1 < n and nums[r] < nums[r + 1]:
                lo = r + 1
            else:
                hi = mid
    return lo
```
