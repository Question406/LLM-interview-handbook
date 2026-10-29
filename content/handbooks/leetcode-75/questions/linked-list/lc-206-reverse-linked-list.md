---
id: lc-206-reverse-linked-list
section: linked-list
order: 3
level: S
title: LC 206 · 反转链表
quick: >-
  迭代用三个指针：`prev=None`、`cur=head`，每步先存 `nxt`，再把 `cur.next` 指向 `prev`，三者一起前进，`cur`
  走空时 `prev` 就是新头。时间 $O(n)$，额外空间 $O(1)$；递归版要 $O(n)$ 栈，所以面试默认写迭代。
tags:
  - Linked List
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 206. Reverse Linked List
    url: 'https://leetcode.com/problems/reverse-linked-list/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定有限、无环单链表的头节点 `head`，反转整条链表的方向。原来的尾节点成为新头节点，原来的头节点成为新尾节点，沿 next 访问时节点顺序与原来完全相反。

### 输入与输出

实现 `reverseList(head) -> ListNode | None`，通过调整原节点的 next 连接返回新头节点，不改动节点值；新尾节点的 next 必须为 None。空链表返回 None，只有一个节点时仍返回该节点。

### 约束

- 节点数在 0 到 5000 之间。
- `-5000 <= Node.val <= 5000`。
- 示例数组按头到尾的顺序表示节点值，实际接口使用节点对象。

### 示例

```text
输入：head = [1,2,3,4,5]
输出：[5,4,3,2,1]
```

[LeetCode 原题](https://leetcode.com/problems/reverse-linked-list/description/)

## 解题思路与参考答案

## 题意

给单链表头节点 `head`，反转整条链表并返回新头。节点数 $0 \le n \le 5000$。进阶要求迭代和递归都会写。

## 思路

我会写迭代版，用三个指针一边走一边把指针拧过来，额外空间 $O(1)$。递归版要 $O(n)$ 的栈，$n$ 到 $5000$ 时 Python 默认递归上限 $1000$ 会爆，所以面试我默认写迭代，递归当追问。题目要改的是节点的连接顺序，只改节点值不满足要求。

迭代时维护一个不变式，`prev` 是已反转部分的头，`cur` 是未处理部分的头。每步先 `nxt = cur.next` 存住后继，不存的话改完指针就丢了；再 `cur.next = prev`，然后 `prev, cur` 各前进一步。`cur` 为空时整条链反转完，`prev` 是原尾，也就是新头。

拿 `1 → 2 → 3 → 4 → 5` 走一遍。第一步 1 的 `next` 指向 `None`，`prev` 到 1、`cur` 到 2；第二步 2 指回 1；依次做下去，处理完 5 之后 `cur` 变空，返回 `prev`，得到 `5 → 4 → 3 → 2 → 1`。

递归版的想法是先反转 `head.next` 之后的部分，拿到新头；这时 `head.next` 是反转段的尾，令 `head.next.next = head`、`head.next = None`。代码放在追问里。

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


def reverseList(head: Optional[ListNode]) -> Optional[ListNode]:
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev


if __name__ == "__main__":
    assert to_list(reverseList(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert to_list(reverseList(from_list([1, 2]))) == [2, 1]
    assert to_list(reverseList(from_list([]))) == []
    assert to_list(reverseList(from_list([7]))) == [7]
    assert to_list(reverseList(from_list(list(range(5000))))) == list(
        range(4999, -1, -1)
    )
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(reverseList(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
assert to_list(reverseList(from_list([1, 2]))) == [2, 1]
assert to_list(reverseList(from_list([]))) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。递归版额外空间 $O(n)$。

## Edge Cases

空链表时循环一次都不进，返回 `None`。

单节点走一步后 `prev` 就是它自己，`next` 被置成 `None`。

原头节点反转后是尾，它的 `next` 必须是 `None`，否则会和第二个节点成环；迭代第一步已经处理了。

## 追问

**递归怎么写？**
递归到最后一个节点，把它作为新头一路返回；回溯时让后继指回自己，再断开自己的 `next`。不断开的话，原头和第二个节点之间会成环。

```python
def reverseListRec(head):
    if head is None or head.next is None:
        return head
    new_head = reverseListRec(head.next)
    head.next.next = head
    head.next = None
    return new_head
```

**只反转第 `left` 到 `right` 段（LC 92）呢？**
用哑结点走到 `left` 的前驱 `pred`，段内第一个节点 `cur` 固定不动，把 `cur.next` 反复头插到 `pred` 后面，做 `right-left` 次。本质上是在 `pred` 后面重复做本题的一步。

```python
def reverseBetween(head, left, right):
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
```

孪生和那题（`lc-2130-maximum-twin-sum-of-a-linked-list`）也要先反转后半段，用的就是这里的迭代写法。
