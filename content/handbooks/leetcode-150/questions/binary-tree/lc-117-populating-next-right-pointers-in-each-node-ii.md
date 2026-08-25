---
id: lc-117-populating-next-right-pointers-in-each-node-ii
section: binary-tree
order: 7
level: A
title: LC 117 · 填充每个节点的下一个右侧节点指针 II
quick: >-
  任意二叉树。层序当然行；更省空间：用当前层已建好的 `next` 串起下一层，哑节点当层头。时间
  $O(n)$，额外空间 $O(1)$（不计递归）。
tags:
  - Tree
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 117. 填充每个节点的下一个右侧节点指针 II
    url: https://leetcode.cn/problems/populating-next-right-pointers-in-each-node-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

节点含 `left`、`right`、`next`。把每一层从左到右用 `next` 连起来，最右指向 `None`。不是完美二叉树，孩子可能缺失。

## 思路

队列层序最直接：每层按出队顺序把前一个的 `next` 指当前。

常数空间：当前层已经是 `next` 链表。遍历这一层，用哑节点把下一层孩子依次接上，然后跳到下一层头。LC 116 的「必有两个孩子」这里不成立，必须跳过空孩子。

## 参考代码

```python
from __future__ import annotations

from typing import Optional


class Node:
    def __init__(
        self,
        val: int = 0,
        left: Optional["Node"] = None,
        right: Optional["Node"] = None,
        next: Optional["Node"] = None,
    ):
        self.val = val
        self.left = left
        self.right = right
        self.next = next


def connect(root: Optional[Node]) -> Optional[Node]:
    dummy = Node(0)
    cur = root
    while cur:
        dummy.next = None
        tail = dummy
        while cur:
            if cur.left:
                tail.next = cur.left
                tail = tail.next
            if cur.right:
                tail.next = cur.right
                tail = tail.next
            cur = cur.next
        cur = dummy.next
    return root


if __name__ == "__main__":
    n4, n5, n7 = Node(4), Node(5), Node(7)
    n2, n3 = Node(2, n4, n5), Node(3, None, n7)
    n1 = Node(1, n2, n3)
    connect(n1)
    assert n1.next is None
    assert n2.next is n3 and n3.next is None
    assert n4.next is n5 and n5.next is n7 and n7.next is None
    assert connect(None) is None
    print("ok")
```

## 复杂度

时间 $O(n)$。用已建 `next` 时额外空间 $O(1)$；层序队列最坏 $O(n)$。

## 边界

- 空树：返回 `None`。
- 缺左或缺右：哑节点串下一层时必须跳过空孩子。
- 底层不连续（中间有空）：靠当前层 `next` 跳到右侧第一个有孩子的节点，不能假设 `next.left` 一定存在。

## 追问

- **完美二叉树（LC 116）？** 每层都满、必有两个孩子，不必哑节点。当前节点：`left.next = right`；若还有 `next`，则 `right.next = next.left`。一层用 `next` 走完后，下沉到 `node.left`。时间 $O(n)$，额外空间 $O(1)$。本题孩子可能缺失，这个写法会空指针。

```python
def connect(root):
    node = root
    while node and node.left:
        cur = node
        while cur:
            cur.left.next = cur.right
            if cur.next:
                cur.right.next = cur.next.left
            cur = cur.next
        node = node.left
    return root
```

- **为何不用父指针？** 当前层已经用 `next` 串成链表，遍历这一层就能按从左到右的顺序碰到下一层所有孩子，相当于「这一层的父节点序列」。哑节点 `tail` 专门接孩子，层尾自然停。父指针不会更快，还要改节点结构。
