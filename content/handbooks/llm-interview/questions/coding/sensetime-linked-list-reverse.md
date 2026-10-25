---
id: sensetime-linked-list-reverse
section: coding
order: 192
level: B
title: 商汤多模态一面：链表反转如何处理输入输出？
quick: >-
  迭代用三指针 `prev, cur, nxt` 原地反转，返回新头。先处理空表和单节点；输入如果是数组，要自己建表，反转后再序列化输出。用递归的话要主动说明 $O(n)$ 的栈，长链表会溢出。
tags:
  - SenseTime
  - Coding
  - Linked List
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 商汤 多模态大模型算法实习一面
    url: https://www.nowcoder.com/feed/main/detail/bc02d116feb54a46a8b85a46f620f9e6
    type: candidate-first-hand
---

## 题目描述

反转一条无环单链表，返回反转后的头节点；同时提供一个便于本地标准输入练习的字符串token入口。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `reverse_list(head)` 和 `reverse_from_tokens(tokens)`。链表节点含整数val和next，head可为None；tokens是合法整数的字符串列表。main读取空白分隔的这些整数。

### 输出与约束

`reverse_list`重新连接原节点，返回原尾节点，不修改节点值。`reverse_from_tokens`把输入建立成链表并返回反转后的整数列表。main把结果以单个空格连接后输出一行；空输入输出空行。

### 示例

```text
tokens=["1","2","3"] -> [3,2,1]
对应标准输入：1 2 3
标准输出：3 2 1
空链表 reverse_list(None) -> None，空tokens -> []。
```

## 解题思路与参考答案

核心就是 206 的三指针迭代，`nxt=cur.next; cur.next=prev; prev=cur; cur=nxt`，循环结束时 `prev` 是新头。这题额外要求处理输入输出，所以还要自己从 stdin 建表，反转后再打印出来。

这是商汤多模态大模型算法实习一面的题，来自牛客候选人原帖，可信度 A，原话是**“手撕题：链表反转，需要处理输入输出”**。现场常见的要求是从 stdin 读一串整数，建表、反转、打印，比如输入 `1 2 3 4 5`，输出 `5 4 3 2 1`。动手前先约定分隔符和空输入怎么处理。多模态岗也会出中等难度的数据结构题，算法卡壳会盖过项目讲述。

## 思路

建表按输入顺序尾插，用一个哑头会简单些。反转就是上面那四步，输出时再扫一遍打印。空输入是打空行还是什么都不打，开口问一句。

递归也能写，但要说明有 $O(n)$ 的栈，超长链表用迭代。面试官接着追问反转 $[l,r]$ 或两两反转时，用的还是这段子程序。

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

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert reverse_from_tokens(["1", "2", "3", "4", "5"]) == [5, 4, 3, 2, 1]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$（不算建表），读写各扫一遍。递归写法额外 $O(n)$ 栈，超长输入不稳。

## 追问

**要测哪些边界？**
空输入、单节点、已经逆序。还要先问清分隔符是空格、逗号还是一行一个，空输入打空行还是不打。

**反转 $[l,r]$ 怎么做？**
先走到 $l$ 的前驱，把这一段当 206 反转完，再接回去。

**两两交换（24）呢？**
每两个一组反转，小心别断链。

**输入是数组，能不能原地反转？**
数组反转用双指针就行；但题目要的是链表，就自己建表，只调一个 `list.reverse()` 交差是不行的。
