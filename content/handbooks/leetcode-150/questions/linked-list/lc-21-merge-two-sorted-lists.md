---
id: lc-21-merge-two-sorted-lists
section: linked-list
order: 3
level: S
title: LC 21 · 合并两个有序链表
quick: >-
  哑结点加双指针：谁小接谁，接完把剩余整段挂上。时间
  $O(m+n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 21. 合并两个有序链表
    url: https://leetcode.cn/problems/merge-two-sorted-lists/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

两个升序链表，合并成一条仍升序的链表。可以改原节点指针，不必新建值节点。

## 思路

哑结点 `dummy`，`cur` 指向已合并段的尾巴。比较两头，较小的接到 `cur` 后面并前进。一条走完后，把另一条剩余直接挂上。

递归也能写：每次返回较小头并接到递归结果上，但多 $O(m+n)$ 栈。面试默认迭代。相等时接哪边都行，保持稳定可优先 `list1`。

## 参考代码

```python
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


def from_list(vals: List[int]) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next


def to_list(head: Optional[ListNode]) -> List[int]:
    out: List[int] = []
    while head:
        out.append(head.val)
        head = head.next
    return out


def mergeTwoLists(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            cur.next = list1
            list1 = list1.next
        else:
            cur.next = list2
            list2 = list2.next
        cur = cur.next
    cur.next = list1 or list2
    return dummy.next


if __name__ == "__main__":
    assert to_list(mergeTwoLists(from_list([1, 2, 4]), from_list([1, 3, 4]))) == [1, 1, 2, 3, 4, 4]
    assert to_list(mergeTwoLists(from_list([]), from_list([]))) == []
    assert to_list(mergeTwoLists(from_list([]), from_list([0]))) == [0]
    print("ok")
```

## 复杂度

时间 $O(m+n)$，额外空间 $O(1)$。每个节点被接一次。

## 边界

- 一表为空：直接返回另一表，`cur.next = list1 or list2` 覆盖。
- 两表等长交错：每次比较接较小头，稳定写法优先 `list1`。
- 一表整体更小：循环中一直接这一表，最后挂上另一表整段。
- 两表都空：返回 `None`。

## 追问

- **$k$ 条有序链表（LC 23）？** 不要循环 $k-1$ 次两两扫，那是 $O(Nk)$。小根堆每次弹最小头结点，把它的后继再压回去，时间 $O(N\log k)$，$N$ 为总结点数。Python 结点不可比，堆里放 `(val, i, node)` 用下标打破平局。分治是相邻两条按本题合并，层数 $\log k$，复杂度相同。独立卡见 `lc-23-merge-k-sorted-lists`。

```python
import heapq

def mergeKLists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    dummy = ListNode()
    cur = dummy
    while heap:
        _, i, node = heapq.heappop(heap)
        cur.next = node
        cur = cur.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

- **数组版（LC 88）？** 链表没有尾部空位，只能从左接。数组若 `nums1` 尾部预留了 $n$ 个空位，应从右往左三指针填，谁大写谁，避免覆盖未读元素。时间 $O(m+n)$，额外空间 $O(1)$。从左直接写会覆盖 `nums1` 里还没比较的数。独立卡见 `lc-88-merge-sorted-array`。

```python
def merge(nums1, m, nums2, n):
    i, j, k = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i -= 1
        else:
            nums1[k] = nums2[j]
            j -= 1
        k -= 1
```
