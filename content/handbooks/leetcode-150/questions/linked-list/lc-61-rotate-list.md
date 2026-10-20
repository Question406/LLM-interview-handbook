---
id: lc-61-rotate-list
section: linked-list
order: 9
level: A
title: LC 61 · 旋转链表
quick: >-
  先求长 $n$，令 $k \bmod n$。尾接回头成环，再走到新尾（第 $n-k$ 个）断开。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 61. 旋转链表
    url: https://leetcode.cn/problems/rotate-list/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

把链表向右旋转 $k$ 位：每个节点移到后继位置，原尾接到原头。例如 `1,2,3,4,5` 且 $k=2$ 得到 `4,5,1,2,3`。

## 思路

空表、单节点或 $k=0$ 直接返回。扫一遍得长度 $n$ 和尾指针。$k \bmod n$，若为 $0$ 不必动。否则把尾节点接到头形成环。新尾是原链表的第 $n-k$ 个节点，新头是它的后继；把新尾的 `next` 置空即可断开。

右旋 $k$ 等价于把后 $k$ 个整段搬到前面。先成环再断开，指针少、不易断链。

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


def rotateRight(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    if head is None or head.next is None or k == 0:
        return head
    n = 1
    tail = head
    while tail.next:
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    tail.next = head
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    return new_head


if __name__ == "__main__":
    assert to_list(rotateRight(from_list([1, 2, 3, 4, 5]), 2)) == [4, 5, 1, 2, 3]
    assert to_list(rotateRight(from_list([0, 1, 2]), 4)) == [2, 0, 1]
    assert to_list(rotateRight(from_list([1]), 99)) == [1]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。求长一遍，再走 $n-k$ 步。

## 边界

- $k$ 是 $n$ 的倍数：取模后为 $0$，原表不动。
- $k \gt n$：必须先 $k \bmod n$，否则走过界。
- 空表 / 单节点：直接返回。
- $k=0$：不旋转。成环前先取模，避免白转一圈。

## 追问

- **改成左旋 $k$？** 左旋 $k$ 等价于右旋 $n-k$。先 $k \bmod n$，再调用这题 `rotateRight(head, n - k)`；若取模后为 $0$ 仍直接返回。也可以成环后走到新尾（第 $k$ 个）断开，新头是它的后继。时间仍 $O(n)$。别对 $k$ 再取一次反，容易把方向转错。白板我先画 `1,2,3,4,5` 左旋 $2$ 得到 `3,4,5,1,2`。

```python
def rotateLeft(head, k):
    if head is None or head.next is None or k == 0:
        return head
    n, tail = 1, head
    while tail.next:
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    return rotateRight(head, n - k)
```

- **数组右旋（LC 189）？** 数组有下标，不必成环。三次反转：$k \bmod n$ 后整体反转，再反转前 $k$ 个，再反转后 $n-k$ 个。时间 $O(n)$，额外空间 $O(1)$。环状替换也能 $O(1)$，但要处理环的个数。独立卡见 `lc-189-rotate-array`。链表没有下标，才用「成环再在 $n-k$ 处断开」。

```python
def rotateArray(nums, k):
    n = len(nums)
    k %= n

    def reverse(lo, hi):
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo += 1
            hi -= 1

    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)
```
