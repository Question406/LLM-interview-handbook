---
id: ali-algo-list-family
section: alibaba-oa
order: 31
level: A
title: 阿里手撕：反转链表、K 组翻转、重排链表怎么一条线讲？
quick: >-
  三道题共用一个子程序：206 用 `pre, cur` 迭代反转，25 是「数 K 个 → 反转这一段 → 接回去」，143
  是找中点、反转后半、交错合并。我会先画指针再写代码，空表、单节点、$k=1$、奇数长度这些 edge cases 开口先讲。
tags:
  - Alibaba
  - 链表
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 反转链表
    url: 'https://leetcode.cn/problems/reverse-linked-list/'
    type: primary
  - title: 2026 校招高频题总览
    url: 'https://www.cnblogs.com/autodriver/p/19829365'
    type: secondary
---

## 题目描述

本卡包含三个独立的单链表操作：反转整条链表、每 k 个节点一组反转，以及首尾交替重排。链表节点包含整数 `val` 和后继指针 `next`，输入没有环。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `reverse_list(head)`、`reverse_k_group(head, k)`、`reorder_list(head)`。`head` 可以为 `None`；分组参数 `k` 为正整数。示例中的列表只表示沿 next 访问到的节点值。

### 输出与约束

前两个函数返回新头节点；分组反转时不足 k 个节点的最后一段保持原样。`reorder_list` 原地把 L0→L1→…→Ln 改成 L0→Ln→L1→Ln-1→…，返回 `None`。只改变原节点的连接，不改变其值，也不得产生环。

### 示例

```text
原链：[1, 2, 3, 4, 5]
reverse_list 后：[5, 4, 3, 2, 1]
reverse_k_group，k=2 后：[2, 1, 4, 3, 5]
对新建原链执行 reorder_list 后：[1, 5, 2, 4, 3]
```

## 解题思路与参考答案

这三道（LeetCode 206 / 25 / 143，阿里校招技术面的高频手撕）我会当成一道题讲：先把 206 的三指针反转写熟，再把它当子程序接到 25 和 143 上。面试官常从 206 加约束一路推到 25、143，考的是指针不丢，算不上三道新题。开写之前，我会先把空表、单节点、$k=1$、奇数长度这几个 edge cases 说清楚。

206 维护 `pre, cur` 两个指针。每一步先抓住 `nxt=cur.next`，再把 `cur.next` 拧到 `pre`，然后整体往前挪一格。循环结束时 `pre` 就是新头。要是先改了 `cur.next` 才想起去拿下一个节点，后面的链表就丢了，所以白板上我会先画三格。

25 从哑节点出发，每次先数满 $k$ 个；数不够就原样返回，不足 $k$ 的尾巴不翻。数够了就把这一段按 206 的方式反转，新头接到上一段的尾巴上，段尾再接回剩下的链表。$k=1$ 相当于什么都没做。

143 先用快慢指针找中点，奇数长度时中点留在前半；然后断开后半并反转，再按 $A_0,B_0,A_1,B_1,\ldots$ 交错合并。合并时别把后半接到自己身上。

## 代码

```python
from __future__ import annotations

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


def reverse_list(head: Optional[ListNode]) -> Optional[ListNode]:
    pre, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = pre
        pre = cur
        cur = nxt
    return pre


def _kth(cur: Optional[ListNode], k: int) -> Optional[ListNode]:
    while cur and k:
        cur = cur.next
        k -= 1
    return cur


def reverse_k_group(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    group_prev = dummy
    while True:
        kth = _kth(group_prev, k)
        if kth is None:
            break
        group_next = kth.next
        prev, cur = group_next, group_prev.next
        while cur is not group_next:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        new_tail = group_prev.next
        group_prev.next = kth
        group_prev = new_tail
    return dummy.next


def reorder_list(head: Optional[ListNode]) -> None:
    if head is None or head.next is None:
        return
    slow, fast = head, head
    while fast.next and fast.next.next:
        slow = slow.next
        fast = fast.next.next
    second = reverse_list(slow.next)
    slow.next = None
    first = head
    while second:
        n1, n2 = first.next, second.next
        first.next = second
        second.next = n1
        first, second = n1, n2


if __name__ == "__main__":
    assert to_list(reverse_list(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
    assert to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
    assert to_list(reverse_k_group(from_list([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
    h = from_list([1, 2, 3, 4, 5])
    reorder_list(h)
    assert to_list(h) == [1, 5, 2, 4, 3]
    print("ok")
```

三道题都是时间 $O(n)$、空间 $O(1)$。206 写成递归要额外 $O(n)$ 的栈；25 的迭代写法里每个节点只进出常数次；143 是找中点、反转、合并各扫一遍。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert to_list(reverse_list(from_list([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

## 追问

**要反转 $[l,r]$ 这一段，或者两两交换呢？**
还是 206 那个子程序，先走到段的前驱，再反转这一段接回去。

**`k` 比链表还长怎么办？**
一组都凑不满，原样返回。206 和 143 碰到空表或单节点也直接返回。

**链表在分布式存储里损坏了，能靠这些操作修吗？**
不能。反转和重排是本地的指针手术，只改拓扑。存储损坏要先靠校验和与副本把数据修回来。
