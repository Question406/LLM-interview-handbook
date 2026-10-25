---
id: lc-92-reverse-linked-list-ii
section: linked-list
order: 5
level: A
title: LC 92 · 反转链表 II
quick: "哑结点走到 `left` 的前驱，然后用头插法做 `right-left` 次，每次把区间里的下一个节点拧到前驱后面。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 92. 反转链表 II
    url: https://leetcode.cn/problems/reverse-linked-list-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定单链表和两个位置 left、right，把从第 left 个节点到第 right 个节点这一整段的连接顺序反转，其他位置不变。位置从 1 开始计数，反转可能包含头节点。

### 输入与输出

实现 `reverseBetween(head, left, right) -> ListNode`，返回修改后的头节点。要调整原链表节点的连接，保留每个节点的值；示例用 next 链中的值序列展示结果。

### 约束与约定

- 节点数 `1 <= n <= 500`。
- 节点值在 `[-500,500]`。
- `1 <= left <= right <= n`。

### 示例

```text
输入：head = [1,2,3,4,5], left = 2, right = 4
输出：[1,4,3,2,5]
```

示例只把位置 2 到 4 的 [2,3,4] 反转成 [4,3,2]。

[官方原题与完整题面](https://leetcode.com/problems/reverse-linked-list-ii/description/)。

## 解题思路与参考答案

## 题意

单链表，把第 `left` 到第 `right` 个节点反转（下标从 $1$ 开始），其余节点的相对顺序不变，返回新头。

## 思路

我用「前驱固定、后继头插」来做，一遍走完。先加一个哑结点，这样 `left=1` 从头开始反转时也有前驱。`pred` 从哑结点走 `left-1` 步，停在反转区间前面。`cur` 固定指向原区间的第一个节点，每次取出它的后继，插到 `pred` 后面，重复 `right-left` 次，区间就完全反过来了。

拿 `[1, 2, 3, 4, 5]`、`left=2`、`right=4` 走一遍。`pred` 停在 1，`cur` 是 2。第一次把 3 插到 1 后面，变成 1、3、2、4、5；第二次把 4 插到 1 后面，变成 1、4、3、2、5，做完了。

也可以先切断子段、整段反转再接回去，只是要管的指针更多。

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


def reverseBetween(head: Optional[ListNode], left: int, right: int) -> Optional[ListNode]:
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


if __name__ == "__main__":
    assert to_list(reverseBetween(from_list([1, 2, 3, 4, 5]), 2, 4)) == [1, 4, 3, 2, 5]
    assert to_list(reverseBetween(from_list([5]), 1, 1)) == [5]
    assert to_list(reverseBetween(from_list([1, 2, 3]), 1, 3)) == [3, 2, 1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(reverseBetween(from_list([1, 2, 3, 4, 5]), 2, 4)) == [1, 4, 3, 2, 5]
assert to_list(reverseBetween(from_list([5]), 1, 1)) == [5]
assert to_list(reverseBetween(from_list([1, 2, 3]), 1, 3)) == [3, 2, 1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。走到 `right` 就够了，不用扫完整张表。

## 边界

- `left == right` 时内层循环零次，原表不变。
- 从头反转（`left=1`）时，哑结点让 `pred` 停在 dummy，新头是原来的第 `right` 个节点。
- 反转段贴着尾巴时，`cur.next` 最后接到 `None`。
- `left=1` 且 `right=n` 时退化成整表反转。

## 追问

**整表反转（LC 206）怎么写？**
三指针迭代，`prev=None`、`cur=head`，每次把 `cur.next` 拧向 `prev`，三个一起前进，最后 `prev` 就是新头。时间 $O(n)$，额外空间 $O(1)$。递归是先翻后面，再把当前节点接到尾上，栈 $O(n)$。这题的头插法，就是在 `pred` 后面反复做 206 的一步。别靠改结点值来「反转」。

```python
def reverseList(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev
```

**每 $k$ 个一组翻（LC 25）呢？**
从哑结点出发，先数够 $k$ 个再把这一段反转并接回，不足 $k$ 个保持原序。反转时把段后的节点当成「空」，段尾就会自动接上剩下的链表；再把前驱接到新头，本组的新尾当下一组的前驱。时间 $O(n)$。这题是任意区间 `[left, right]`，LC 25 是固定块长。独立卡见 `lc-25-reverse-nodes-in-k-group`。

```python
def reverseKGroup(head, k):
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
```
