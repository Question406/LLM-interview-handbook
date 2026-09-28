---
id: lc-25-reverse-nodes-in-k-group
section: linked-list
order: 6
level: S
title: LC 25 · K 个一组翻转链表
quick: >-
  从哑结点出发，先数够 $k$ 个再反转这一段并接回；不足 $k$ 保持原序。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 25. K 个一组翻转链表
    url: https://leetcode.cn/problems/reverse-nodes-in-k-group/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

每 $k$ 个节点一组翻转链表。最后不足 $k$ 个的保持原顺序。只能改指针，不能改节点值。

## 思路

哑结点 `dummy`。每次从当前组前驱出发数 $k$ 步：数不到就结束。数到则把这一段按 206 反转。反转时把后继当「空」，这样段尾自动接到剩余链表。再把前驱接到新头，本组新尾变成下一组前驱。

别先整表反转再切。开口先说「先数后翻，不够不翻」。

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


def reverseKGroup(head: Optional[ListNode], k: int) -> Optional[ListNode]:
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


if __name__ == "__main__":
    assert to_list(reverseKGroup(from_list([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
    assert to_list(reverseKGroup(from_list([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
    assert to_list(reverseKGroup(from_list([1]), 1)) == [1]
    print("ok")
```

## 复杂度

时间 $O(n)$：每个节点最多被数一次、反转一次。额外空间 $O(1)$。

## 边界

- $k=1$：每组一个，反转恒等，原表不变。
- $n$ 恰整除 $k$：最后一组也翻，没有残留。
- 最后一组不足 $k$：数不到 $k$ 个直接返回，保持原序。
- 整表长度小于 $k$：一遍就返回原头。

## 追问

- **两两交换（LC 24）？** 就是 $k=2$ 的特化，不必通用数 $k$ 步。哑结点 `pred`，每次取 `a=pred.next`、`b=a.next`，把 `pred -> b -> a -> 后续` 接好，再让 `pred=a` 处理下一对。奇数长度时最后一只保持不动。时间 $O(n)$，额外空间 $O(1)$。递归写法 `head.next` 接 `swapPairs(head.next.next)` 再把 `head` 接到后面，栈 $O(n)$，面试默认迭代。

```python
def swapPairs(head):
    dummy = ListNode(0, head)
    pred = dummy
    while pred.next and pred.next.next:
        a = pred.next
        b = a.next
        pred.next, a.next, b.next = b, b.next, a
        pred = a
    return dummy.next
```

- **从后往前按 $k$ 组翻？** 先求长度 $n$，跳过前 $n \bmod k$ 个不翻，对剩余后缀跑这题。也可以先整表反转、再按组翻、再整表反转回来，三次都是 $O(n)$。第一种少一次整表反转，指针更直观。注意 $n \bmod k=0$ 时与从前往后相同。别先按组翻再整体反转，那不是「从尾对齐」。

```python
def reverseKGroupFromEnd(head, k):
    n, cur = 0, head
    while cur:
        n += 1
        cur = cur.next
    skip = n % k
    dummy = ListNode(0, head)
    pred = dummy
    for _ in range(skip):
        pred = pred.next
    pred.next = reverseKGroup(pred.next, k)
    return dummy.next
```
