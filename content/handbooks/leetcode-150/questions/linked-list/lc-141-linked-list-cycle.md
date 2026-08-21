---
id: lc-141-linked-list-cycle
section: linked-list
order: 1
level: S
title: LC 141 · 环形链表
quick: >-
  Floyd 快慢指针：慢走一步、快走两步。相遇则有环，快指针到空则无环。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 141. 环形链表
    url: https://leetcode.cn/problems/linked-list-cycle/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给链表头节点，判断是否存在环：某个节点的 `next` 能再次指向先前节点。有环返回 `true`，否则 `false`。

## 思路

Floyd 判环。`slow` 每次走一步，`fast` 走两步。有环时两者必在环内相遇；无环则 `fast` 先到空。

哈希记访问过的节点也能判，但要 $O(n)$ 空间。面试先讲清「相对速度为 $1$，环上必相遇」，再写循环条件 `fast and fast.next`。

## 参考代码

```python
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


def from_list(vals: List[int], pos: int = -1) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    nodes: List[ListNode] = []
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
        nodes.append(cur)
    if pos >= 0:
        cur.next = nodes[pos]
    return dummy.next


def hasCycle(head: Optional[ListNode]) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


if __name__ == "__main__":
    assert hasCycle(from_list([3, 2, 0, -4], 1)) is True
    assert hasCycle(from_list([1, 2], 0)) is True
    assert hasCycle(from_list([1], -1)) is False
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。无环扫一遍；有环时快慢在环内相遇，圈数不超过环长。

## 边界

- 空表 / 单节点无环：`fast` 或 `fast.next` 为空，返回假。
- 自环（`pos=0`）：第一步 `slow` 与 `fast` 都回到头，立刻相遇。
- 环在尾、入口在中间：相遇点一般不是入口。
- 两个节点互指：第一步后相遇。

## 追问

- **环的入口在哪（LC 142）？** Floyd 相遇后不要停。设头到入口 $a$ 步、入口到相遇点 $b$ 步、环长 $c$。慢指针走了 $a+b$，快指针走了 $a+b+kc=2(a+b)$，故 $a=kc-b$，即「从头走 $a$ 步」与「从相遇点再走 $a$ 步」同时到达入口。因此把一指针放回头，两指针每次一步，再相遇就是入口。无环返回 `None`。时间 $O(n)$，额外空间 $O(1)$。不要把相遇点当成入口。

```python
def detectCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            p = head
            while p is not slow:
                p = p.next
                slow = slow.next
            return p
    return None
```

- **为何快慢指针必相遇、不会跳过？** 相对速度为 $1$（快每次多走一格）。无环时快指针先到空，正确返回假。有环后两者都在环上，环上距离每步缩短 $1$，模 $c$ 意义下必碰到 $0$，不会跳过对方。因为节点是离散的，快指针走两步、慢指针走一步，相对位移恰好 $1$，不存在「跨过慢指针」的情况。哈希记访问过的节点也能判环，但要 $O(n)$ 空间，面试默认 Floyd。

```python
def hasCycleHash(head):
    seen = set()
    while head:
        if head in seen:
            return True
        seen.add(head)
        head = head.next
    return False
```
