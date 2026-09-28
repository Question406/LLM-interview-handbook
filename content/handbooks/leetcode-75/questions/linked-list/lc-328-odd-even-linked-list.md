---
id: lc-328-odd-even-linked-list
section: linked-list
order: 2
level: A
title: LC 328 · 奇偶链表
quick: >-
  两条链交替拆：`odd` 接奇数位，`even` 接偶数位，记住偶链头，最后把奇链尾接到偶链头。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 328. Odd Even Linked List
    url: https://leetcode.com/problems/odd-even-linked-list/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

单链表，把所有奇数位置（第 $1, 3, 5, \dots$ 个，按位置不是按值）的节点放到前面，偶数位置放到后面，两组内部保持原相对顺序。要求 $O(1)$ 额外空间、$O(n)$ 时间，返回新头。

## 思路

原地拆成两条链。`odd` 从头开始，`even` 从第二个开始，另存 `even_head`。每轮 `odd.next = even.next`，`odd` 前进；再 `even.next = odd.next`，`even` 前进。循环条件是 `even and even.next`：偶链指针还有下一个奇数节点可以挂。结束后 `odd` 停在奇链尾，接上 `even_head`。

偶链尾在最后一步会被置成 `odd.next`，而这时奇链已经走完，值为 `None`，所以不会成环。用额外数组收集再重连也能做，但违反 $O(1)$ 空间要求。

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


def oddEvenList(head: Optional[ListNode]) -> Optional[ListNode]:
    if head is None:
        return None
    odd, even = head, head.next
    even_head = even
    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return head


if __name__ == "__main__":
    assert to_list(oddEvenList(from_list([1, 2, 3, 4, 5]))) == [1, 3, 5, 2, 4]
    assert to_list(oddEvenList(from_list([2, 1, 3, 5, 6, 4, 7]))) == [2, 3, 6, 7, 1, 5, 4]
    assert to_list(oddEvenList(from_list([]))) == []
    assert to_list(oddEvenList(from_list([1]))) == [1]
    assert to_list(oddEvenList(from_list([1, 2]))) == [1, 2]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 空链表或单节点：直接返回。
- 两个节点：循环一次不进，`odd.next` 重新接回偶链头，原样不变。
- 长度奇偶不同：偶数长度时 `even` 走到尾节点停，奇数长度时 `even` 变成 `None` 停，两种都不会成环。

## 追问

- **按值的奇偶分组而不是按位置？** 同样两条链，但要用两个哑结点，因为第一个奇数值未必是头。遍历时按 `val % 2` 挂到对应链尾，最后奇链尾接偶链头、偶链尾置 `None`。这就是 LC 86 分隔链表的套路。

```python
def partitionByParity(head):
    odd_dummy, even_dummy = ListNode(), ListNode()
    o, e = odd_dummy, even_dummy
    while head:
        if head.val % 2:
            o.next = head
            o = o.next
        else:
            e.next = head
            e = e.next
        head = head.next
    e.next = None
    o.next = even_dummy.next
    return odd_dummy.next
```

- **为什么循环条件是 `even and even.next`？** 每轮要读 `even.next` 作为下一个奇数节点，`even` 本身不能为空；`even.next` 为空说明奇数节点已经用完，再走就会把 `odd` 推到 `None`，最后一步 `odd.next = even_head` 会报错。
