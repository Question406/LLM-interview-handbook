---
id: lc-26-remove-duplicates-from-sorted-array
section: array-string
order: 3
level: S
title: LC 26 · 删除有序数组中的重复项
quick: >-
  数组已排序，相同元素相邻。慢指针写不重复值：当前与已写入末尾不同才写入。返回新长度。时间
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
  - title: 26. 删除有序数组中的重复项
    url: https://leetcode.cn/problems/remove-duplicates-from-sorted-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

非递减数组 `nums`，原地删掉重复项，每个值只留一次。返回新长度 $k$，并保证 `nums[:k]` 仍非递减且无重复。

## 思路

有序保证重复段连续。慢指针 `slow` 指向下一个可写位置；`fast` 扫全数组。若 `nums[fast] != nums[slow-1]`，写入并推进 `slow`。第一个元素必保留，从下标 $1$ 开始比即可。

哈希去重要 $O(n)$ 空间，且打乱顺序。白板我会强调：有序才能 $O(1)$ 原地。

## 参考代码

```python
from typing import List


def removeDuplicates(nums: List[int]) -> int:
    if not nums:
        return 0
    slow = 1
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow - 1]:
            nums[slow] = nums[fast]
            slow += 1
    return slow


if __name__ == "__main__":
    a = [1, 1, 2]
    k = removeDuplicates(a)
    assert k == 2 and a[:k] == [1, 2]
    b = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
    k = removeDuplicates(b)
    assert k == 5 and b[:k] == [0, 1, 2, 3, 4]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。一次扫描。

## 边界

- 长度为 $1$：没有重复可删，返回 $1$。
- 全部相同：只留一个，返回 $1$。
- 全部不同：`slow` 每次都写，返回 $n$。

## 追问

- **每个值最多保留两次（LC 80）？** 仍是慢指针原地写。`slow` 表示下一个可写位置；当前值与 `nums[slow - 2]` 不同才写入（前两个名额还没占满时 `slow < 2` 也写）。有序保证相同值相邻，所以跟倒数第 $2$ 个比就知道这个值已经留了几次。时间 $O(n)$，额外空间 $O(1)$。写成 `slow - 1` 会退化成本题只留一次。独立卡见 `lc-80-remove-duplicates-from-sorted-array-ii`。

```python
def removeDuplicates_at_most_two(nums):
    slow = 0
    for x in nums:
        if slow < 2 or x != nums[slow - 2]:
            nums[slow] = x
            slow += 1
    return slow
```

- **数组无序？** 有序是 $O(1)$ 原地的前提。无序要去重且保相对顺序：用哈希记录出现过的值，慢指针写第一次出现的，时间 $O(n)$，额外空间 $O(n)$。若允许打乱顺序：先排序再走本题指针，时间 $O(n\log n)$，额外空间 $O(1)$。不要无序还硬套 `nums[slow - 1]`，不相邻的重复会漏。
