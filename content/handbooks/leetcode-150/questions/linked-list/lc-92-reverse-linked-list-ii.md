---
id: lc-92-reverse-linked-list-ii
section: linked-list
order: 5
level: A
title: LC 92 · 反转链表 II
quick: >-
  哑结点走到 `left` 前驱，再把头插法做 `right-left` 次：把后继逐个拧到前驱后面。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 92. 反转链表 II
    url: https://leetcode.cn/problems/reverse-linked-list-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

单链表，把第 `left` 到第 `right` 个节点反转（下标从 $1$ 计），其余相对顺序不变，返回新头。

## 思路

哑结点防 `left=1` 改头。`pred` 先走 `left-1` 步，停在反转段前驱。`cur` 是段内第一个节点，保持不动；随后把 `cur.next` 头插到 `pred` 后面，重复 `right-left` 次。

也可先切断子段、整段反转再接回，指针更多。白板我会讲「前驱固定、后继头插」。

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


def reverseBetween(head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
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


if __name__ == "__main__":
    assert to_list(reverseBetween(from_list([1, 2, 3, 4, 5]), 2, 4)) == [1, 4, 3, 2, 5]
    assert to_list(reverseBetween(from_list([5]), 1, 1)) == [5]
    assert to_list(reverseBetween(from_list([1, 2, 3]), 1, 3)) == [3, 2, 1]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。走到 `right` 即可，不必扫完整表。

## 边界

- `left == right`：内层循环零次，原表不变。
- 整表反转（`left=1`）：哑结点让 `pred` 停在 dummy，新头是原 `right`。
- 反转段贴尾：`cur.next` 最终接到 `None`。
- `left=1` 且 `right=n`：退化为整表反转。

## 追问

- **整表反转（LC 206）？** 三指针迭代：`prev=None`，`cur=head`，每次把 `cur.next` 拧到 `prev`，三人一起前进，最后 `prev` 是新头。时间 $O(n)$，额外空间 $O(1)$。递归是先翻后面再把当前接到尾上，栈 $O(n)$。这题头插法就是把这段当成「在 `pred` 后面反复做 206 的一步」。别改结点值来「反转」。

```python
def reverseList(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev
```

- **每 $k$ 个一组翻（LC 25）？** 从哑结点出发，先数够 $k$ 个再反转这一段并接回；不足 $k$ 保持原序。反转时把段后后继当「空」，段尾会自动接到剩余链表。再把前驱接到新头，本组新尾变成下一组前驱。时间 $O(n)$。独立卡见 `lc-25-reverse-nodes-in-k-group`。这题是任意 `[left, right]`，LC 25 是固定块长。

```python
def reverseKGroup(head, k):
    dummy = ListNode(0, head)
    pred = dummy
    while True:
        tail = pred
        for _ in range(k):
            tail = tail.next
            if tail is None:
                return dummy.next
        nxt = tail.next
        prev, cur = nxt, pred.next
        while cur is not nxt:
            tmp = cur.next
            cur.next = prev
            prev = cur
            cur = tmp
        new_tail = pred.next
        pred.next = tail
        pred = new_tail
```
