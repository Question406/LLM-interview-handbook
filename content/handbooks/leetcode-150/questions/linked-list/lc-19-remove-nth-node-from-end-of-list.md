---
id: lc-19-remove-nth-node-from-end-of-list
section: linked-list
order: 7
level: S
title: LC 19 · 删除链表的倒数第 N 个结点
quick: >-
  哑结点加快慢指针：快指针先走 $n$ 步，再一起走，快到末尾时慢在待删前驱。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 19. 删除链表的倒数第 N 个结点
    url: https://leetcode.cn/problems/remove-nth-node-from-end-of-list/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

删除单链表的倒数第 $n$ 个结点，返回头结点。$n$ 保证合法。

## 思路

先求长再走 `len-n` 要两遍。一遍做法：哑结点，快指针先走 $n$ 步，然后快慢同步。当 `fast.next` 为空，`slow` 正好是待删前驱，执行 `slow.next = slow.next.next`。

哑结点保证删头时不用特判。白板我会先画「快慢间距为 $n$」。

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


def removeNthFromEnd(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next
    while fast.next:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next


if __name__ == "__main__":
    assert to_list(removeNthFromEnd(from_list([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
    assert to_list(removeNthFromEnd(from_list([1]), 1)) == []
    assert to_list(removeNthFromEnd(from_list([1, 2]), 1)) == [1]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。快指针走完全表一次。

## 边界

- 删头（$n$ 等于链长）：哑结点让 `slow` 停在 dummy，`dummy.next` 跳过原头。
- 删尾（$n=1$）：快指针先走 $1$ 步到原头，同步后 `slow` 在倒数第二个。
- 只剩一个节点：删头且删尾，返回空。
- $n$ 保证合法，不必处理 $n$ 过大。

## 追问

- **只要倒数第 $k$ 个节点本身、不必删？** 快指针先走 $k$ 步（从 `head` 出发，不要哑结点），然后快慢同步，快到空时慢就是目标。间距仍是 $k$，只是少一次前驱操作。若 $k$ 等于链长，快先走完，慢仍在头，正确。时间 $O(n)$，额外空间 $O(1)$。先求长再走 `len-k` 也行，但两遍。

```python
def kthFromEnd(head, k):
    fast = slow = head
    for _ in range(k):
        fast = fast.next
    while fast:
        fast = fast.next
        slow = slow.next
    return slow
```

- **双向链表或数组呢？** 数组下标随机访问，倒数第 $n$ 就是 `arr[len(arr)-n]`，删的话 `pop` 或切片即可。双向链表有尾指针时从尾巴走 $n-1$ 步到目标，再改 `prev/next`。单链表没有前驱也没有下标，才需要「快慢间距为 $n$」这一招。白板我会把三种结构的代价说清：数组 $O(1)$ 定位、$O(n)$ 删除；双链 $O(n)$ 定位、$O(1)$ 删除；单链定位删除都 $O(n)$ 但一遍扫完。
