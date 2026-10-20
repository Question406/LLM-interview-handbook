---
id: lc-23-merge-k-sorted-lists
section: divide-conquer
order: 4
level: S
title: LC 23 · 合并 K 个升序链表
quick: >-
  $k$ 条有序链表。小根堆每次弹最小头结点，或分治两两归并。时间
  $O(N\log k)$，$N$ 为总结点数。
tags:
  - Heap
  - Linked List
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 23. 合并 K 个升序链表
    url: https://leetcode.cn/problems/merge-k-sorted-lists/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`lists` 里有 $k$ 条升序链表，可能含空表。合并成一条升序链表。

## 思路

小根堆保存各链表当前最小的未处理节点 `(val, i, node)`。每次弹出最小节点接到结果，再将它的后继入堆。值相同时使用下标 $i$ 比较，避免 Python 直接比较节点对象。

分治：相邻两条按 LC 21 合并，区间递归，层数 $\log k$。两种都是 $O(N\log k)$。不要循环 $k-1$ 次两两扫，那是 $O(Nk)$。

堆先写，分治口头补一句。

## 参考代码

```python
import heapq
from typing import List, Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def mergeKLists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
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

    ans = mergeKLists([from_list([1, 4, 5]), from_list([1, 3, 4]), from_list([2, 6])])
    assert to_list(ans) == [1, 1, 2, 3, 4, 4, 5, 6]
    assert mergeKLists([]) is None
    assert mergeKLists([None]) is None
    print("ok")
```

## 复杂度

时间 $O(N\log k)$，堆大小至多 $k$。额外空间 $O(k)$。分治栈 $O(\log k)$。

## 边界

- $k=0$ 或 `lists` 为空：堆为空，返回 `None`。
- 全是空表：入堆循环全部跳过，同样 `None`。
- 只有一条：堆里只有一个头，弹出整条接上即可。
- 某条特别长：该表结点会陆续入堆，堆大小仍 $\le k$，不会退化成 $O(Nk)$。

## 追问

- **分治两两归并？** 不必堆。把 $k$ 条按下标对半切，递归合并左右两组，底层两条用 LC 21 哨兵归并。递归树 $\log k$ 层，每层每个结点只被看一次，总时间 $O(N\log k)$，额外栈 $O(\log k)$。顺序循环 `merge(ans, lists[i])` 会让已合并前缀越来越长，是 $O(Nk)$，要主动对比。

```python
def mergeKListsDC(lists):
    if not lists:
        return None

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
        return dummy.next

    def dc(lo, hi):
        if lo == hi:
            return lists[lo]
        mid = (lo + hi) // 2
        return merge(dc(lo, mid), dc(mid + 1, hi))

    return dc(0, len(lists) - 1)
```

- **数组版（$k$ 路有序数组合并）？** 同样小根堆：`(值, 数组下标, 元素下标)`，弹出后把该数组下一个推进去，时间 $O(N\log k)$。两路且 `nums1` 尾部有空位就是 LC 88 的从右三指针。分治两两 `merge` 也可以，缓冲 $O(N)$。独立卡见 `lc-88-merge-sorted-array`。

```python
def mergeKArrays(arrs):
    heap, ans = [], []
    for i, a in enumerate(arrs):
        if a:
            heapq.heappush(heap, (a[0], i, 0))
    while heap:
        v, i, j = heapq.heappop(heap)
        ans.append(v)
        if j + 1 < len(arrs[i]):
            heapq.heappush(heap, (arrs[i][j + 1], i, j + 1))
    return ans
```
