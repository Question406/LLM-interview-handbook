---
id: lc-2130-maximum-twin-sum-of-a-linked-list
section: linked-list
order: 4
level: A
title: LC 2130 · 链表最大孪生和
quick: >-
  快慢指针找后半段起点，原地反转后半段，再和前半段并排走，逐对求和取最大。时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Linked List
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2130. Maximum Twin Sum of a Linked List
    url: https://leetcode.com/problems/maximum-twin-sum-of-a-linked-list/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

链表长度 $n$ 为偶数（$2 \le n \le 10^5$），下标 $i$ 与 $n-1-i$ 的节点互为孪生，孪生和是两者值之和。返回所有孪生和中的最大值。

## 思路

孪生对是「第 $i$ 个和倒数第 $i$ 个」，单链表不能倒着走，所以把后半段反转，反转后后半段的第 $i$ 个就是原来的倒数第 $i$ 个。`slow`、`fast` 同从头起跑，`fast` 走到头时 `slow` 停在下标 $n/2$，即后半段起点。反转 `slow` 开头的这段，再用两个指针并排走 $n/2$ 步求最大和。

最省事的写法是把值倒进数组，再用 `arr[i] + arr[n-1-i]`，额外空间 $O(n)$。面试官要 $O(1)$ 空间时就用反转；如果要求不改原链表，最后再把后半段反转回去接上。

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


def pairSum(head: Optional[ListNode]) -> int:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    prev = None
    while slow:
        nxt = slow.next
        slow.next = prev
        prev = slow
        slow = nxt
    best = 0
    a, b = head, prev
    while b:
        best = max(best, a.val + b.val)
        a = a.next
        b = b.next
    return best


if __name__ == "__main__":
    assert pairSum(from_list([5, 4, 2, 1])) == 6
    assert pairSum(from_list([4, 2, 2, 3])) == 7
    assert pairSum(from_list([1, 100000])) == 100001
    assert pairSum(from_list([1, 1, 1, 1, 1, 1])) == 2
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- $n=2$：`slow` 停在第二个节点，反转后只有一对。
- 反转后前半段的尾仍指向原后半段第一个节点（现在是反转段的尾），并排走时以 `b` 为空作终止条件，就不会多算。
- 节点值都是正数，`best` 从 $0$ 起没问题；若允许负数要从 $-\infty$ 起。

## 追问

- **不允许修改链表？** 用栈：先把前半段值压栈，再走后半段逐个弹栈配对，额外空间 $O(n)$。或者照常反转，算完再反转一次后半段恢复原状，仍是 $O(1)$ 空间。

```python
def pairSumStack(head):
    slow = fast = head
    stack = []
    while fast and fast.next:
        stack.append(slow.val)
        slow = slow.next
        fast = fast.next.next
    best = 0
    while slow:
        best = max(best, stack.pop() + slow.val)
        slow = slow.next
    return best
```

- **判断回文链表（LC 234）？** 同一骨架：找中点、反转后半段、并排比较值是否相等。奇数长度时中间节点落在后半段起点，反转后它是后半段的尾，前半段先走完即结束，不影响判断。反转写法见 `lc-206-reverse-linked-list`。
