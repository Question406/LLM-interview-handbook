---
id: sensetime-linked-list-reverse
section: coding
order: 192
level: B
title: 商汤多模态一面：链表反转如何处理输入输出？
quick: >-
  迭代三指针 `prev, cur, nxt` 原地反转，返回新头。先处理空表和单节点；若输入是数组要自己建表再序列化输出。不要递归到栈溢出还不提复杂度。
tags:
  - SenseTime
  - Coding
  - Linked List
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 商汤 多模态大模型算法实习一面
    url: https://www.nowcoder.com/feed/main/detail/bc02d116feb54a46a8b85a46f620f9e6
    type: candidate-first-hand
---

## 真题 / 考点说明

- 公司：商汤
- 岗位：多模态大模型算法实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“手撕题：链表反转，需要处理输入输出”**

现场常要求从 stdin 读一串整数、建表、反转、再打印。先约定分隔符和空输入。核心仍是 206 三指针。多模态岗仍会出中等数据结构，算法卡壳会盖过项目讲述。

## 思路

建表：按输入顺序尾插，或哑头。反转：`nxt=cur.next; cur.next=prev; prev=cur; cur=nxt`，结束时 `prev` 是新头。输出：再扫一遍打印。空输入打印空行或什么都不打，开口问一句。

递归也能写，但要提 $O(n)$ 栈；超长链表用迭代。追问反转 $[l,r]$、两两反转，还是这段子程序。

## 参考代码

```python
from __future__ import annotations

import sys
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
    prev, cur = None, head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev


def reverse_from_tokens(tokens: List[str]) -> List[int]:
    if not tokens:
        return []
    head = from_list([int(x) for x in tokens])
    return to_list(reverse_list(head))


def main() -> None:
    tokens = sys.stdin.read().split()
    vals = reverse_from_tokens(tokens)
    if vals:
        print(" ".join(str(x) for x in vals))
    else:
        print()


if __name__ == "__main__":
    assert reverse_from_tokens(["1", "2", "3", "4", "5"]) == [5, 4, 3, 2, 1]
    assert reverse_from_tokens([]) == []
    assert reverse_from_tokens(["7"]) == [7]
    head = reverse_list(from_list([1, 2]))
    assert to_list(head) == [2, 1]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$（不含建表）。递归写法额外 $O(n)$ 栈，超长输入不稳。读写各扫一遍。

## 边界与追问

1. 空输入、单节点、已逆序。先问分隔符是空格、逗号还是一行一个；空输入打空行还是不打。
2. 追问反转 $[l,r]$：走到 $l$ 的前驱，把子段当 206 做完再接回去。追问两两交换（24）：每两个一组，注意断链。
3. 追问「输入是数组能否原地」：数组反转双指针即可；题目要链表就自己建表，不要只 `list.reverse()` 交差。
