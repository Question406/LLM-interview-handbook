---
id: lc-206-reverse-linked-list
section: linked-list
order: 3
level: S
title: LC 206 · 反转链表
quick: >-
  三指针迭代：`prev=None`、`cur=head`，每步先存 `nxt`，再把 `cur.next` 拧向 `prev`，三者前进，最后 `prev`
  是新头。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 206. Reverse Linked List
    url: https://leetcode.com/problems/reverse-linked-list/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给单链表头节点 `head`，反转整条链表并返回新头。节点数 $0 \le n \le 5000$。进阶要求迭代和递归都会写。

## 思路

迭代时维护一个不变式：`prev` 是已反转部分的头，`cur` 是未处理部分的头。每步先 `nxt = cur.next` 存住后继，否则改指针后就丢了；再 `cur.next = prev`，然后 `prev, cur` 各前进一步。`cur` 为空时整条链反转完，`prev` 是原尾、新头。

递归版：先反转 `head.next` 之后的部分，拿到新头；此时 `head.next` 是反转段的尾，令 `head.next.next = head`、`head.next = None`。递归栈 $O(n)$，$n$ 到 $5000$ 时 Python 默认递归上限 $1000$ 会爆，所以面试我默认写迭代，递归当追问。改节点值来「反转」不算数。

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


def reverseList(head: Optional[ListNode]) -> Optional[ListNode]:
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev


if __name__ == "__main__":
    assert to_list(reverseList(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert to_list(reverseList(from_list([1, 2]))) == [2, 1]
    assert to_list(reverseList(from_list([]))) == []
    assert to_list(reverseList(from_list([7]))) == [7]
    assert to_list(reverseList(from_list(list(range(5000))))) == list(range(4999, -1, -1))
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。递归版额外空间 $O(n)$。

## 边界

- 空链表：循环不进，返回 `None`。
- 单节点：一步后 `prev` 是它自己，`next` 被置成 `None`。
- 原头节点反转后是尾，`next` 必须是 `None`，否则会和第二个节点成环；迭代第一步已经处理了。

## 追问

- **递归怎么写？** 递归到最后一个节点作为新头一路返回；回溯时让后继指回自己，再断开自己的 `next`。不断开会在原头和第二个节点之间成环。

```python
def reverseListRec(head):
    if head is None or head.next is None:
        return head
    new_head = reverseListRec(head.next)
    head.next.next = head
    head.next = None
    return new_head
```

- **只反转第 `left` 到 `right` 段（LC 92）？** 哑结点走到 `left` 前驱 `pred`，段内第一个节点 `cur` 固定不动，把 `cur.next` 反复头插到 `pred` 后面，做 `right-left` 次。本质是在 `pred` 后面重复做本题的一步。孪生和那题（`lc-2130-maximum-twin-sum-of-a-linked-list`）也要先反转后半段，用的就是这里的迭代写法。

```python
def reverseBetween(head, left, right):
    dummy = ListNode(0, head)
    pred = dummy
    for _ in range(left - 1):
        pred = pred.next
    cur = pred.next
    for _ in range(right - left):
        nxt = cur.next
        cur.next = nxt.next
        nxt.next = pred.next
        pred.next = nxt
    return dummy.next
```
