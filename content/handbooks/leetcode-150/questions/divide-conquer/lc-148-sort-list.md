---
id: lc-148-sort-list
section: divide-conquer
order: 2
level: A
title: LC 148 · 排序链表
quick: >-
  快慢指针切半，递归排序两段再归并。时间 $O(n\log n)$。自顶向下栈
  $O(\log n)$；自底向上可做到额外空间 $O(1)$。
tags:
  - Linked List
  - Merge Sort
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 148. 排序链表
    url: https://leetcode.cn/problems/sort-list/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

单链表按结点值升序排序。要求时间 $O(n\log n)$。

## 思路

链表不能按下标随机访问，快排分区麻烦，归并最合适。快慢指针找中点，从中点断开，左右各自排序，再按 LC 21 归并。

`slow` 走一步、`fast` 走两步；`fast` 从 `head.next` 出发，断开后左段更短或等长。空表或单结点直接返回。

自底向上按 $1,2,4,\ldots$ 段长两两合并，可把递归栈去掉。自顶向下先写。

## 参考代码

```python
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def sortList(head: Optional[ListNode]) -> Optional[ListNode]:
    if not head or not head.next:
        return head
    slow, fast = head, head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    mid = slow.next
    slow.next = None
    return merge(sortList(head), sortList(mid))


def merge(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    while a and b:
        if a.val <= b.val:
            cur.next, a = a, a.next
        else:
            cur.next, b = b, b.next
        cur = cur.next
    cur.next = a or b
    return dummy.next


if __name__ == "__main__":
    def from_list(vals):
        dummy = ListNode()
        cur = dummy
        for v in vals:
            cur.next = ListNode(v)
            cur = cur.next
        return dummy.next

    def to_list(head):
        out = []
        while head:
            out.append(head.val)
            head = head.next
        return out

    assert to_list(sortList(from_list([4, 2, 1, 3]))) == [1, 2, 3, 4]
    assert to_list(sortList(from_list([-1, 5, 3, 4, 0]))) == [-1, 0, 3, 4, 5]
    assert to_list(sortList(from_list([]))) == []
    print("ok")
```

## 复杂度

时间 $O(n\log n)$：$\log n$ 层，每层遍历 $O(n)$。自顶向下额外栈 $O(\log n)$。

## 边界

- 空表 / 单结点：`not head or not head.next` 直接返回，不必切。
- 已有序：归并比较永远走左支，仍是 $O(n\log n)$ 次比较，只是交换少。
- 完全逆序：每层归并都从右段取，结果正确。
- 含负数：只比较结点值，与符号无关。

## 追问

- **$O(1)$ 额外空间（自底向上）？** 自顶向下递归栈 $O(\log n)$。改成迭代：先数长度 $n$，用哑结点挂整表。段长 `step = 1, 2, 4, \ldots`，每一轮把链表切成若干长为 `step` 的有序段（第一轮单结点已有序），相邻两段做 LC 21 归并，用 `prev` 把归并结果接回去。`split(head, n)` 切断前 $n$ 个并返回后继。全程只有常数指针，额外空间 $O(1)$，时间仍 $O(n\log n)$。

```python
def sortListBottomUp(head):
    n, p = 0, head
    while p:
        n += 1
        p = p.next
    dummy = ListNode(0, head)
    step = 1
    while step < n:
        prev, cur = dummy, dummy.next
        while cur:
            left = cur
            right = split(left, step)
            cur = split(right, step)
            merged, tail = merge(left, right)
            prev.next = merged
            prev = tail
        step *= 2
    return dummy.next


def split(head, n):
    for _ in range(n - 1):
        if not head:
            return None
        head = head.next
    if not head:
        return None
    rest = head.next
    head.next = None
    return rest


def merge(a, b):
    dummy = ListNode()
    cur = dummy
    while a and b:
        if a.val <= b.val:
            cur.next, a = a, a.next
        else:
            cur.next, b = b, b.next
        cur = cur.next
    cur.next = a or b
    while cur.next:
        cur = cur.next
    return dummy.next, cur
```

- **数组版？** 数组能按下标切中点，归并要 $O(n)$ 缓冲；或直接 `sort`。链表没有下标，切半必须快慢指针（或先数长度再走 `n//2` 步）。链表归并是改 `next`，不必额外数组，这是链表归并相对数组的优势。
