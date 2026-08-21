---
id: lc-2-add-two-numbers
section: linked-list
order: 2
level: S
title: LC 2 · 两数相加
quick: >-
  低位在前，按位相加并维护进位。任一链表或进位未尽就继续建节点。时间
  $O(\max(m,n))$，额外空间 $O(1)$（不含答案链）。
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 2. 两数相加
    url: https://leetcode.cn/problems/add-two-numbers/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

两个非空链表表示非负整数，每位逆序存储（头结点是个位）。返回它们的和，同样低位在前。每个节点只存一位数字。

## 思路

同时扫描两表，当前位之和加上进位，写出个位、留下十位。任一表走完后另一表继续加；最后若进位非零再补一个节点。

不要先转成整数：位数可达上百，会溢出。哑结点省掉「第一个节点特判」。面试先说「低位对齐 + 进位」，再写 `while l1 or l2 or carry`。

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


def addTwoNumbers(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    carry = 0
    while l1 or l2 or carry:
        if l1:
            carry += l1.val
            l1 = l1.next
        if l2:
            carry += l2.val
            l2 = l2.next
        cur.next = ListNode(carry % 10)
        cur = cur.next
        carry //= 10
    return dummy.next


if __name__ == "__main__":
    assert to_list(addTwoNumbers(from_list([2, 4, 3]), from_list([5, 6, 4]))) == [7, 0, 8]
    assert to_list(addTwoNumbers(from_list([0]), from_list([0]))) == [0]
    assert to_list(addTwoNumbers(from_list([9, 9, 9, 9, 9, 9, 9]), from_list([9, 9, 9, 9]))) == [
        8, 9, 9, 9, 0, 0, 0, 1
    ]
    print("ok")
```

## 复杂度

时间 $O(\max(m,n))$，额外空间 $O(1)$（不含新链表）。每位最多访问一次。

## 边界

- 一表更长：短表走完后继续加长表与进位。
- 全是 $9$：进位一路传到最高位，最后多一个节点 $1$。
- 两表都是 `[0]`：循环一次写出 $0$，进位清零。
- 一表为空：题面非空，若放宽则当成 $0$ 处理。

## 追问

- **高位在前（LC 445）？** 不能直接对齐个位。先把两条链反转，当成原题来加，再把结果反转回来。也可以用两个栈依次压入，弹出时从低位加，头插建答案（每次新节点当头）。不要先转成整数，位数过长会溢出。反转写法额外空间 $O(1)$（不计答案）；栈写法 $O(m+n)$。反转原表要确认是否允许改输入。

```python
def reverseList(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev

def addTwoNumbersHigh(l1, l2):
    return reverseList(addTwoNumbers(reverseList(l1), reverseList(l2)))
```

- **数组版？** 从尾巴对齐：`i, j` 从末尾往前，当前位加进位，结果头插或先放进列表再反转。最后若进位非零，答案会多一位。时间 $O(\max(m,n))$。注意不要用字符串转整数。两数组等长且无进位时长度不变；`[9,9]+[1]` 得到 `[1,0,0]`。

```python
def addArrays(a, b):
    i, j, carry, out = len(a) - 1, len(b) - 1, 0, []
    while i >= 0 or j >= 0 or carry:
        if i >= 0:
            carry += a[i]
            i -= 1
        if j >= 0:
            carry += b[j]
            j -= 1
        out.append(carry % 10)
        carry //= 10
    out.reverse()
    return out
```
