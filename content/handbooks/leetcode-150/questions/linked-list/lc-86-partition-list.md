---
id: lc-86-partition-list
section: linked-list
order: 10
level: A
title: LC 86 · 分隔链表
quick: >-
  小于 $x$ 走一条链，其余走另一条，保持相对顺序，再把左尾接右头。右尾必须置空。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 86. 分隔链表
    url: https://leetcode.cn/problems/partition-list/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

重排链表，使所有小于 $x$ 的节点都在大于等于 $x$ 的节点之前。两类内部相对顺序不变。例如 `1,4,3,2,5,2` 且 $x=3$ 得到 `1,2,2,4,3,5`。

## 思路

两条哑链：`left` 收小于 $x$ 的，`right` 收其余。原序扫描，节点原样接到对应尾巴。扫完把 `right` 尾巴置空（否则可能成环），再把 `left` 尾巴接到 `right` 头。

别用交换值：题目允许改指针，且要保持稳定顺序。白板我会先画两条链再拼接。

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


def partition(head: Optional[ListNode], x: int) -> Optional[ListNode]:
    left_d = ListNode()
    right_d = ListNode()
    left, right = left_d, right_d
    while head:
        if head.val < x:
            left.next = head
            left = left.next
        else:
            right.next = head
            right = right.next
        head = head.next
    right.next = None
    left.next = right_d.next
    return left_d.next


if __name__ == "__main__":
    assert to_list(partition(from_list([1, 4, 3, 2, 5, 2]), 3)) == [1, 2, 2, 4, 3, 5]
    assert to_list(partition(from_list([2, 1]), 2)) == [1, 2]
    assert to_list(partition(from_list([1]), 0)) == [1]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个节点改一次 `next`。

## 边界

- 全部小于 $x$：右链为空，`left` 接到 `None`，相对顺序不变。
- 全部不小于 $x$：左链为空，返回右链头。
- $x$ 比所有值都小：全部走右链。
- 单节点：走其中一条，另一条为空。

## 追问

- **为什么右链尾巴必须置空？** 右链最后一个结点原来的 `next` 可能指向一个已被分到左链的结点。若不 `right.next = None`，拼接后会从右尾回到左链，成环。左尾接下来就要接到右头，所以左尾不必预先置空。这块容易栽。空右链时 `right` 仍是哑结点，置空是 `dummy.next = None`，无害。白板我会画 `1,4,3,2` 且 $x=3$ 时 `4` 的旧后继是 `3`，但 `2` 已被接到左边。

```python
# 扫完必须：
right.next = None
left.next = right_d.next
```

- **数组版稳定划分？** 开两个数组分别收 $\lt x$ 与 $\ge x$，再拼接，稳定且 $O(n)$。双指针从两端交换不稳定：右边一个小的被换到左边时，越过了中间元素。原地稳定划分需要块交换或额外 $O(n)$ 缓冲，面试不必硬写。链表这题已经是稳定的 $O(1)$ 额外空间，这是链表比数组好写的地方。

```python
def partitionArray(nums, x):
    left = [v for v in nums if v < x]
    right = [v for v in nums if v >= x]
    return left + right
```
