---
id: lc-148-sort-list
section: divide-conquer
order: 2
level: A
title: LC 148 · 排序链表
quick: "链表排序用归并：快慢指针找中点断开，两段递归排好，再按 LC 21 合并，时间 $O(n\\log n)$。自顶向下有 $O(\\log n)$ 的递归栈；要额外空间 $O(1)$，就改成自底向上按段长 1、2、4 迭代合并。"
tags:
  - Linked List
  - Merge Sort
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 148. 排序链表
    url: https://leetcode.cn/problems/sort-list/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定单链表头节点 `head`，把链表按节点值的非递减顺序排序，并返回排序后的头节点。链表中的重复值都必须保留；空链表也是合法输入。

### 输入与输出

实现 `sortList(head) -> ListNode | None`。输入和输出均为链表节点对象，示例数组仅表示从头到尾的节点值。要求时间为 O(n log n)；原题还可进一步要求常数级额外空间。

### 约束

- 节点数在 0 到 `5 * 10^4` 之间。
- `-10^5 <= Node.val <= 10^5`。
- 链表为有限、无环的单链表。

### 示例

```text
输入：head = [4,2,1,3]
输出：[1,2,3,4]
```

[LeetCode 原题](https://leetcode.com/problems/sort-list/description/)

## 解题思路与参考答案

## 题意

单链表按结点值升序排序，要求时间 $O(n\log n)$。

## 思路

我会用归并排序。链表没法按下标随机访问，快排的分区写起来很别扭；归并只需要找中点和合并两条有序链表，这两件事链表都很顺手。

中点用快慢指针找：`slow` 走一步、`fast` 走两步，`fast` 从 `head.next` 出发，这样断开后左段更短或等长。拿 `4 → 2 → 1 → 3` 来说，`slow` 停在 `2`，从这里断开得到 `4 → 2` 和 `1 → 3`，两段各自递归排成 `2 → 4`、`1 → 3`，再按 LC 21 的方式合并成 `1 → 2 → 3 → 4`。空表或单结点直接返回，这是递归的出口。

白板上先写自顶向下的递归版。想把递归栈也去掉，可以自底向上按 $1,2,4,\ldots$ 的段长两两合并，这个放在追问里讲。

## 参考代码

```python
from typing import Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def sortList(head: Optional[ListNode]) -> Optional[ListNode]:
    if not head or not head.next:
        return head
    slow, fast = head, head.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    mid = slow.next
    slow.next = None
    return merge(sortList(head), sortList(mid))


def merge(a: Optional[ListNode], b: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    while a and b:
        if a.val <= b.val:
            cur.next, a = a, a.next
        else:
            cur.next, b = b, b.next
        cur = cur.next
    cur.next = a or b
    return dummy.next


if __name__ == "__main__":
    def from_list(vals):
        dummy = ListNode()
        cur = dummy
        for v in vals:
            cur.next = ListNode(v)
            cur = cur.next
        return dummy.next

    def to_list(head):
        out = []
        while head:
            out.append(head.val)
            head = head.next
        return out

    assert to_list(sortList(from_list([4, 2, 1, 3]))) == [1, 2, 3, 4]
    assert to_list(sortList(from_list([-1, 5, 3, 4, 0]))) == [-1, 0, 3, 4, 5]
    assert to_list(sortList(from_list([]))) == []
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
def from_list(vals):
        dummy = ListNode()
        cur = dummy
        for v in vals:
            cur.next = ListNode(v)
            cur = cur.next
        return dummy.next
def to_list(head):
        out = []
        while head:
            out.append(head.val)
            head = head.next
        return out
assert to_list(sortList(from_list([4, 2, 1, 3]))) == [1, 2, 3, 4]
assert to_list(sortList(from_list([-1, 5, 3, 4, 0]))) == [-1, 0, 3, 4, 5]
assert to_list(sortList(from_list([]))) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

一共 $\log n$ 层，每层合并遍历 $O(n)$，所以时间是 $O(n\log n)$。自顶向下的递归栈额外占 $O(\log n)$。

## 边界

空表或只有一个结点时，`not head or not head.next` 直接返回，不用再切。已经有序的输入，归并比较永远走左支，比较次数仍是 $O(n\log n)$，只是交换少。完全逆序时每层归并都从右段取，结果照样正确。含负数也没关系，只比较结点值，和符号无关。

## 追问

**能做到 $O(1)$ 额外空间吗？**
能，改成自底向上的迭代版。自顶向下的递归栈是 $O(\log n)$；迭代版先数出长度 $n$，用哑结点挂住整表。段长 `step = 1, 2, 4, \ldots`，每一轮把链表切成若干长为 `step` 的有序段（第一轮单结点天然有序），相邻两段做 LC 21 归并，再用 `prev` 把归并结果接回去。`split(head, n)` 切断前 $n$ 个结点并返回后继。全程只用常数个指针，额外空间 $O(1)$，时间仍是 $O(n\log n)$。

```python
def sortListBottomUp(head):
    n, p = 0, head
    while p:
        n += 1
        p = p.next
    dummy = ListNode(0, head)
    step = 1
    while step < n:
        prev, cur = dummy, dummy.next
        while cur:
            left = cur
            right = split(left, step)
            cur = split(right, step)
            merged, tail = merge(left, right)
            prev.next = merged
            prev = tail
        step *= 2
    return dummy.next


def split(head, n):
    for _ in range(n - 1):
        if not head:
            return None
        head = head.next
    if not head:
        return None
    rest = head.next
    head.next = None
    return rest


def merge(a, b):
    dummy = ListNode()
    cur = dummy
    while a and b:
        if a.val <= b.val:
            cur.next, a = a, a.next
        else:
            cur.next, b = b, b.next
        cur = cur.next
    cur.next = a or b
    while cur.next:
        cur = cur.next
    return dummy.next, cur
```

**换成数组怎么做？**
数组能按下标直接切中点，但归并要一块 $O(n)$ 的缓冲，或者干脆调 `sort`。链表没有下标，切半只能靠快慢指针（或先数长度再走 `n//2` 步）；好处是链表归并只改 `next`，不用额外数组，这是链表归并相对数组的优势。
