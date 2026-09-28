---
id: lc-88-merge-sorted-array
section: array-string
order: 1
level: S
title: LC 88 · 合并两个有序数组
quick: >-
  `nums1` 尾部预留了 $n$ 个空位。从右往左三指针填，谁大写谁，避免覆盖未读元素。时间
  $O(m+n)$，额外空间 $O(1)$。
tags:
  - Array
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 88. 合并两个有序数组
    url: https://leetcode.cn/problems/merge-sorted-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`nums1` 长度 $m+n$，前 $m$ 个有序，后 $n$ 个空位；`nums2` 长度 $n$ 且有序。把两者合并进 `nums1`，仍非递减。

## 思路

从尾巴填。`i=m-1`、`j=n-1`、`k=m+n-1`。比较 `nums1[i]` 与 `nums2[j]`，较大的写入 `nums1[k]`，对应指针减一。`j` 耗尽即可停：`nums1` 前缀已经就位。`i` 先耗尽则把 `nums2` 剩余段拷进去。

从左往右会覆盖 `nums1` 里还没比较的数。空位在尾部，所以从右往左填。

## 参考代码

```python
from typing import List


def merge(nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    i, j, k = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i -= 1
        else:
            nums1[k] = nums2[j]
            j -= 1
        k -= 1


if __name__ == "__main__":
    a = [1, 2, 3, 0, 0, 0]
    merge(a, 3, [2, 5, 6], 3)
    assert a == [1, 2, 2, 3, 5, 6]
    b = [1]
    merge(b, 1, [], 0)
    assert b == [1]
    c = [0]
    merge(c, 0, [1], 1)
    assert c == [1]
    print("ok")
```

## 复杂度

时间 $O(m+n)$，额外空间 $O(1)$。每个元素最多被写一次。

## 边界

- $m=0$：`nums1` 全是空位，循环会把 `nums2` 整段拷进去。
- $n=0$：`j` 一开始就 $<0$，循环不进，前缀已经是答案。
- `nums2` 全小于 / 全大于 `nums1`：从右填时会先耗尽一侧，另一侧原位不动或整段搬入。

## 追问

- **不能原地改 `nums1`？** 先把 `nums1[:m]` 拷到缓冲 `left`，再从左双指针合并写回。时间仍 $O(m+n)$，额外空间 $O(m)$。也可以新开 $m+n$ 再整体赋回。从左直接往 `nums1` 写会覆盖还没比较的元素，所以要么从右填（本题），要么先拷走有效段。

```python
def merge_with_buffer(nums1, m, nums2, n):
    left = nums1[:m]
    i = j = k = 0
    while i < m and j < n:
        if left[i] <= nums2[j]:
            nums1[k] = left[i]
            i += 1
        else:
            nums1[k] = nums2[j]
            j += 1
        k += 1
    nums1[k : k + (m - i)] = left[i:]
    nums1[k : k + (n - j)] = nums2[j:]
```

- **链表版（LC 21）？** 链表没有尾部空位，不能从右填。用哨兵 `dummy` 和尾指针 `tail`，每次把较小的头结点接到 `tail` 后面；某条耗尽后把另一条整段接上。时间 $O(m+n)$，额外空间 $O(1)$。独立卡见 `lc-21-merge-two-sorted-lists`。

```python
def mergeTwoLists(l1, l2):
    dummy = ListNode(0)
    tail = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next, l1 = l1, l1.next
        else:
            tail.next, l2 = l2, l2.next
        tail = tail.next
    tail.next = l1 or l2
    return dummy.next
```
