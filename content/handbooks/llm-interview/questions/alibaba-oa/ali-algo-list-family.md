---
id: ali-algo-list-family
section: alibaba-oa
order: 31
level: A
title: 阿里手撕：反转链表、K 组翻转、重排链表怎么一条线讲？
quick: >-
  206 是迭代三指针。25 是「数 K 个 → 反转这一段 → 接回去」。143 是找中点、反转后半、交错合并。我会先画指针再写代码。
tags:
  - Alibaba
  - 链表
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 反转链表
    url: https://leetcode.cn/problems/reverse-linked-list/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题 / 考点说明

- 岗位：阿里校招技术面高频手撕
- 对应：LeetCode 206 / 25 / 143

三条题共用同一套指针手术：先会 206 的三指针反转，再把它当成子程序接到 25 和 143 上。空表、单节点、$k=1$、奇数长度，开口我都会先讲。

追问「链表在分布式存储损坏」：先说校验和与副本；反转/重排是本地指针手术，不能当存储修复。

## 思路

206：维护 `pre, cur`。每次先抓住 `nxt=cur.next`，再把 `cur.next` 拧到 `pre`，然后整体前移。循环结束 `pre` 是新头。

25：从哑节点出发，每次先数满 $k$ 个；数不够就原样返回。数够则把这一段按 206 反转，把新头接到上一段尾巴上，再把段尾接到剩余链表。$k=1$ 是恒等变换。

143：慢指针找中点（奇数长度中点留在前半），断开后半并反转，再按 $A_0,B_0,A_1,B_1,\ldots$ 交错。不要在合并时把后半接到自己身上。

## 参考代码

```python
from __future__ import annotations

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


def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    pre, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = pre
        pre = cur
        cur = nxt
    return pre


def _kth(cur: Optional[ListNode], k: int) -> Optional[ListNode]:
    while cur and k:
        cur = cur.next
        k -= 1
    return cur


def reverse_k_group(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        kth = _kth(group_prev, k)
        if kth is None:
            break
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        new_tail = group_prev.next
        group_prev.next = kth
        group_prev = new_tail
    return dummy.next


def reorder_list(head: Optional[ListNode]) -> None:
    if head is None or head.next is None:
        return
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    second = reverse_list(slow.next)
    slow.next = None
    first = head
    while second:
        n1, n2 = first.next, second.next
        first.next = second
        second.next = n1
        first, second = n1, n2


if __name__ == "__main__":
    assert to_list(reverse_list(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
    assert to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
    h = from_list([1, 2, 3, 4, 5])
    reorder_list(h)
    assert to_list(h) == [1, 5, 2, 4, 3]
    print("ok")
```

## 复杂度

- 206：时间 $O(n)$，空间 $O(1)$。递归写法额外 $O(n)$ 栈。
- 25：每节点进出常数次，时间 $O(n)$，空间 $O(1)$（迭代）。
- 143：找中点 + 反转 + 合并各扫一遍，时间 $O(n)$，空间 $O(1)$。

## 边界与追问

1. 空表、单节点、`k` 大于长度：206/143 直接返回；25 不足 $k$ 的尾巴不翻。
2. 追问「反转 $[l,r]$ / 两两交换」：还是 206 子程序，只是先走到段前驱再反转。
3. 追问分布式损坏：校验和与副本修复数据，指针手术只改拓扑，不能当存储修复。
