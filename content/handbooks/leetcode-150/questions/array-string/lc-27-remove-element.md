---
id: lc-27-remove-element
section: array-string
order: 2
level: S
title: LC 27 · 移除元素
quick: >-
  快慢指针：快指针扫全数组，慢指针只写不等于 `val` 的元素。返回慢指针，就是新长度。时间
  $O(n)$，额外空间 $O(1)$。
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

## 题意

给定数组 `nums` 和值 `val`，原地移除所有等于 `val` 的元素，返回移除后的新长度。前 $k$ 个位置放保留元素，相对顺序可保持。

## 思路

快慢指针。`fast` 扫每一个位置；当 `nums[fast] != val` 时，把该值写到 `nums[slow]`，`slow` 加一。扫完后 `slow` 就是新长度。

不必真的删掉尾部垃圾：题目只认前 $k$ 个。白板我会先讲「写指针只前进保留元素」，再写循环。

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

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个元素读一次、最多写一次。

## 边界

- 全是 `val`：`slow` 从不前进，返回 $0$。
- 一个都不是：每个元素都写入，返回 $n$，数组原样。
- 空数组：循环不进，返回 $0$。

## 追问

- **必须保持相对顺序？允许打乱呢？** 上面的快慢指针已经保持相对顺序：保留元素按原先后写到前缀。若题目允许打乱，可以从两端夹：`i` 从左找 `val`，找到就把尾部元素换过来，长度减一，`i` 先不前进，因为换来的也可能是 `val`。`val` 很少时，只在命中时写一次，写次数更少；时间仍 $O(n)$，额外空间 $O(1)$。这块容易栽：交换后立刻 `i += 1`，以及用 `pop` 真删导致尾部下标混乱。判题只认前 $k$ 个，不必清掉后面的垃圾。

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

- **改成删除有序数组里的重复项？** 仍是慢指针写前缀，只是「能不能写」的判定变了。最多留 $1$ 次：当前值与已写的最后一个不同才写，即 LC 26，独立卡见 `lc-26-remove-duplicates-from-sorted-array`。最多留 $2$ 次：与已写的倒数第二个不同才写（或还没写满两个），即 LC 80，独立卡见 `lc-80-remove-duplicates-from-sorted-array-ii`。有序是前提，无序不能只看相邻。时间都 $O(n)$，额外空间 $O(1)$。不要边扫边单独维护「当前值出现了几次」，和 `slow` 不同步时很容易多删或少删。

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
