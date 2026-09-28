---
id: lc-2095-delete-the-middle-node-of-a-linked-list
section: linked-list
order: 1
level: A
title: LC 2095 · 删除链表的中间节点
quick: >-
  快慢指针，让慢指针停在中间节点的前驱：`slow=head`、`fast=head.next.next` 起跑，快的走到头时
  `slow.next` 就是中间，直接跳过。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2095. Delete the Middle Node of a Linked List
    url: https://leetcode.com/problems/delete-the-middle-node-of-a-linked-list/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

长度为 $n$ 的单链表，删除下标为 $\lfloor n/2 \rfloor$ 的节点（下标从 $0$ 计），返回头节点。$n=1$ 时删完为空链表。偶数长度删的是靠后那个中点，例如 $n=4$ 删下标 $2$。

## 思路

删除单链表节点要拿到它的前驱。快慢指针里，`fast` 比 `slow` 先走两步起跑，`slow` 每走一步 `fast` 走两步，`fast` 走到尾时 `slow` 恰好停在下标 $\lfloor n/2 \rfloor - 1$，也就是中间节点的前驱，执行 `slow.next = slow.next.next` 即可。

$n=1$ 没有前驱，单独返回 `None`。朴素做法是先数长度再走 $\lfloor n/2 \rfloor - 1$ 步，也是 $O(n)$，只是扫两遍；面试里我会先写两遍扫描说清楚下标，再换成快慢指针。

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


def deleteMiddle(head: Optional[ListNode]) -> Optional[ListNode]:
    if head is None or head.next is None:
        return None
    slow, fast = head, head.next.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    slow.next = slow.next.next
    return head


if __name__ == "__main__":
    assert to_list(deleteMiddle(from_list([1, 3, 4, 7, 1, 2, 6]))) == [1, 3, 4, 1, 2, 6]
    assert to_list(deleteMiddle(from_list([1, 2, 3, 4]))) == [1, 2, 4]
    assert to_list(deleteMiddle(from_list([2, 1]))) == [2]
    assert to_list(deleteMiddle(from_list([1]))) == []
    assert to_list(deleteMiddle(from_list([1, 2, 3]))) == [1, 3]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- $n=1$：没有前驱，返回 `None`。
- $n=2$：`fast` 起跑就是 `None`，`slow` 停在头，删掉第二个节点。
- 偶数长度：删靠后的中点，起跑差两步正好对齐这个下标。

## 追问

- **返回中间节点而不是删除（LC 876）？** `slow`、`fast` 都从 `head` 起跑，`fast` 走到头时 `slow` 就是中点，偶数长度落在靠后那个。和本题只差起跑位置：想停在前驱就让 `fast` 多走两步。

```python
def middleNode(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

- **只给要删的节点、拿不到头（LC 237）？** 拿不到前驱，就把后继的值拷过来，再删后继：`node.val = node.next.val; node.next = node.next.next`。前提是该节点不是尾节点。这种做法改的是值，节点身份变了，外部若持有后继的引用会出问题，要说明。
