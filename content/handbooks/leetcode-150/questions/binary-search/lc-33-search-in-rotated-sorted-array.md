---
id: lc-33-search-in-rotated-sorted-array
section: binary-search
order: 4
level: S
title: LC 33 · 搜索旋转排序数组
quick: "旋转后 `mid` 两边总有一半有序。`target` 落在有序那一半的值域里就缩到这半，否则去另一半。数组无重复，一次二分，时间 $O(\\log n)$。"
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 33. 搜索旋转排序数组
    url: https://leetcode.cn/problems/search-in-rotated-sorted-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

一个原本严格递增、没有重复元素的整数数组，可能在某个位置切开，再把后半段移到前面。例如 [0,1,2,4,5,6,7] 可以变成 [4,5,6,7,0,1,2]。在这个数组中查找给定目标值。

### 输入与输出

实现 `search(nums, target) -> int`。目标存在时返回它在当前数组中的从 0 开始的下标；不存在则返回 -1。

### 约束与约定

- `1 <= len(nums) <= 5000`。
- 数组各值互异，nums 与 target 的数值均在 `[-10000,10000]`。
- 数组可能没有发生轮转；要求查找时间为 `O(log n)`。

### 示例

```text
输入：nums = [4,5,6,7,0,1,2], target = 0
输出：4
```

示例里 0 在轮转后数组的下标 4。

[官方原题与完整题面](https://leetcode.com/problems/search-in-rotated-sorted-array/description/)。

## 解题思路与参考答案

## 题意

原本升序的互异数组在 [某下标, 末尾] + [开头, 某下标) 处断开重接。在 $O(\log n)$ 内找 `target`，没有返回 $-1$。

## 思路

我会一次二分。旋转后的数组，`mid` 两边总有一半是有序的：`nums[lo] <= nums[mid]` 说明左半有序，否则右半有序。`target` 落在有序那一半的闭区间里就缩进去，不在就丢掉这一半。

拿 `[4,5,6,7,0,1,2]` 找 0。`mid=3` 是 7，`nums[0]=4` 不大于 7，左半有序，但 0 不在 4 到 7 之间，丢掉左半，`lo=4`。`mid=5` 是 1，`nums[4]=0` 不大于 1，左半有序，0 正好落在里面，`hi=4`。`mid=4` 就是 0，返回 4。

先找最小值再在对应段二分也行，是两次 $\log$；一次二分更常见。有重复是 LC 81，相等时只能 `lo += 1`，最坏 $O(n)$。

## 参考代码

```python
from typing import List


def search(nums: List[int], target: int) -> int:
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


if __name__ == "__main__":
    assert search([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search([1], 0) == -1
    assert search([1], 1) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert search([4, 5, 6, 7, 0, 1, 2], 0) == 4
assert search([4, 5, 6, 7, 0, 1, 2], 3) == -1
assert search([1], 0) == -1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log n)$，额外空间 $O(1)$。

## 边界

未旋转时 `nums[lo] \le nums[mid]` 始终成立，退化成普通的有序二分。旋转点在 $1$ 或 $n-1$ 时，有序半几乎是整段，无序半只有一个元素，比较仍然正确。$n=1$ 时一次 `mid == target` 判断就够。目标是最小值或最大值时，会落到断点两侧的值域判断里，不会因为不在有序半中间被漏掉。

## 追问

**有重复（LC 81）怎么办？**
相等时没法丢任何一半，只能 `lo += 1`，两端都相等时还可以同时 `hi -= 1`，最坏 $O(n)$。无重复时 `nums[lo] \le nums[mid]` 能唯一判定左半有序；有重复后，像 `[1,0,1,1,1]` 里 `lo` 和 `mid` 都是 $1$，左半其实是无序的。`nums[mid] == target` 已经在前面返回了，所以丢掉的一定是非目标的副本。全是同一个值且目标不在数组里，就是最坏情况。返回值改成布尔就行。独立卡见 `lc-81`。

```python
def searchDup(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return True
        if nums[lo] == nums[mid]:
            lo += 1
            continue
        if nums[lo] < nums[mid]:
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return False
```

**只找最小值（LC 153）呢？**
不用判断 `target` 在哪一半，只和右端比。`nums[mid] \gt nums[hi]` 说明最小值在 `mid` 右侧，`lo = mid + 1`；否则 `mid` 本身可能就是最小，`hi = mid`；缩到 `lo == hi`。和左端比不好用，未旋转时左端一直最小，没法据此丢掉哪一半。时间 $O(\log n)$。独立卡见 `lc-153-find-minimum-in-rotated-sorted-array`。

```python
def findMin(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]
```
