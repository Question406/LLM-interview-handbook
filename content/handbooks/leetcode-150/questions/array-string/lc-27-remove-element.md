---
id: lc-27-remove-element
section: array-string
order: 2
level: S
title: LC 27 · 移除元素
quick: "用快慢指针：快指针扫全数组，慢指针只写不等于 `val` 的元素，扫完慢指针就是新长度。题目只检查前 $k$ 个位置，后面不用清理。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Array
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 27. 移除元素
    url: https://leetcode.cn/problems/remove-element/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定整数数组 `nums` 和整数 `val`，原地移除所有值等于 `val` 的元素。移除不是要求缩短 Python 列表的实际长度，而是把保留元素安排到数组的有效前缀。

### 接口与输出

实现 `removeElement(nums: List[int], val: int) -> int`，返回保留元素数量 k。调用结束后，`nums[:k]` 必须恰好包含原数组中所有不等于 val 的元素，并保留各自出现次数；这些元素的顺序不限。下标 k 之后的内容不参与判定。

### 合法输入与约束

`0 <= len(nums) <= 100`，`0 <= nums[i] <= 50`，`0 <= val <= 100`。空数组是合法输入，返回 0。

### 示例

```text
输入：nums = [3,2,2,3], val = 3
输出：2, nums = [2,2,_,_]
```

示例输出中的 `_` 表示不检查该位置，不是需要写进数组的字符。

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/remove-element/description/)。

## 解题思路与参考答案

## 题意

给定数组 `nums` 和值 `val`，原地移除所有等于 `val` 的元素，返回移除后的新长度。前 $k$ 个位置放保留元素，相对顺序可保持。

## 思路

我用快慢指针，因为判题只看前 $k$ 个位置，把保留的元素依次写到前缀就行。`fast` 扫每一个位置，`nums[fast] != val` 时把它写到 `nums[slow]`，`slow` 加一；扫完 `slow` 就是新长度。

拿 `[3, 2, 2, 3]`、`val = 3` 走一遍：第一个 $3$ 跳过；两个 $2$ 依次写到下标 $0$、$1$；最后的 $3$ 跳过，返回 $2$，前缀是 `[2, 2]`。

后面的值不用清理。只有遇到保留元素时写指针才前进，这保证前缀里都是有效元素。

## 参考代码

```python
from typing import List


def removeElement(nums: List[int], val: int) -> int:
    slow = 0
    for x in nums:
        if x != val:
            nums[slow] = x
            slow += 1
    return slow


if __name__ == "__main__":
    a = [3, 2, 2, 3]
    k = removeElement(a, 3)
    assert k == 2 and sorted(a[:k]) == [2, 2]
    b = [0, 1, 2, 2, 3, 0, 4, 2]
    k = removeElement(b, 2)
    assert k == 5 and sorted(b[:k]) == [0, 0, 1, 3, 4]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
a = [3, 2, 2, 3]
k = removeElement(a, 3)
assert k == 2 and sorted(a[:k]) == [2, 2]
b = [0, 1, 2, 2, 3, 0, 4, 2]
k = removeElement(b, 2)
assert k == 5 and sorted(b[:k]) == [0, 0, 1, 3, 4]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个元素读一次、最多写一次。

## 边界

全是 `val` 时 `slow` 从不前进，返回 $0$。一个都不是时每个元素都写一遍，返回 $n$，数组原样。空数组循环不进，返回 $0$。

## 追问

**必须保持相对顺序吗？允许打乱呢？**
上面的写法已经保持了相对顺序，保留元素按原来的先后写到前缀。如果允许打乱，可以从两端夹：`i` 从左找 `val`，找到就把尾部元素换过来、长度减一，`i` 先不前进，因为换过来的也可能是 `val`。`val` 很少时只在命中时写一次，写的次数更少；时间仍 $O(n)$，额外空间 $O(1)$。交换后立刻 `i += 1`、或者用 `pop` 真删导致尾部下标混乱，是这版最常见的两个错。判题只认前 $k$ 个，后面的垃圾不必清掉。

```python
def removeElement_swap(nums, val):
    i, n = 0, len(nums)
    while i < n:
        if nums[i] == val:
            n -= 1
            nums[i] = nums[n]
        else:
            i += 1
    return n
```

**改成删除有序数组里的重复项呢？**
还是慢指针写前缀，只是「能不能写」的判定变了。最多留 $1$ 次，就是当前值和已写的最后一个不同才写，即 LC 26，独立卡见 `lc-26-remove-duplicates-from-sorted-array`。最多留 $2$ 次，就是和已写的倒数第二个不同才写（或者还没写满两个），即 LC 80，独立卡见 `lc-80-remove-duplicates-from-sorted-array-ii`。有序是前提，无序时光看相邻会漏。时间都是 $O(n)$，额外空间 $O(1)$。别边扫边单独维护「当前值出现了几次」，它和 `slow` 不同步时很容易多删或少删。

```python
def removeDuplicates(nums):
    slow = 0
    for x in nums:
        if slow == 0 or nums[slow - 1] != x:
            nums[slow] = x
            slow += 1
    return slow


def removeDuplicatesAtMostTwo(nums):
    slow = 0
    for x in nums:
        if slow < 2 or nums[slow - 2] != x:
            nums[slow] = x
            slow += 1
    return slow
```
