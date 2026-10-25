---
id: lc-117-populating-next-right-pointers-in-each-node-ii
section: binary-tree
order: 7
level: A
title: LC 117 · 填充每个节点的下一个右侧节点指针 II
quick: "这题是任意二叉树。层序遍历当然能做；更省空间的写法是用当前层已经连好的 `next` 去串下一层，哑节点当下一层的头，空孩子跳过。时间 $O(n)$，额外空间 $O(1)$（不计递归）。"
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

## 题目描述

给定一棵普通二叉树，每个节点除了 left、right 之外还有 next 指针，初始都为 None。把每个节点的 next 指向同一层中紧邻它右侧的节点；该层最右侧节点的 next 仍为 None。节点可以缺少任意一侧的孩子，不能假设树是满树。

### 输入与输出

实现 `connect(root) -> Node`，直接修改原节点的 next，并返回原树根。输入层序数组中的 null 表示缺失孩子；输出示例把每层沿 next 读出的值连在一起，用 # 标记层结束。

### 约束与约定

- 节点数为 0 到 6000，节点值在 `[-100,100]`。
- 原有 left/right 关系不得改变。
- 进阶要求使用常数额外空间；递归调用栈不计入该要求。

### 示例

```text
输入：root = [1,2,3,4,5,null,7]
输出：[1,#,2,3,#,4,5,7,#]
```

示例最终的 next 链为 1；2→3；4→5→7，各链末尾都指向 None。

[官方原题与完整题面](https://leetcode.com/problems/populating-next-right-pointers-in-each-node-ii/description/)。

## 解题思路与参考答案

## 题意

节点有 `left`、`right`、`next` 三个指针。要把每一层从左到右用 `next` 连起来，每层最右边的节点指向 `None`。这棵树不保证是完美二叉树，孩子可能缺失。

## 思路

最直接的是队列层序，每层按出队顺序把前一个节点的 `next` 指向当前节点，但队列最坏要 $O(n)$ 空间。我会写常数空间的版本：上一轮做完之后，当前层已经是一条 `next` 链表，顺着它走一遍就能从左到右碰到下一层的所有孩子。用一个哑节点和尾指针 `tail` 把这些孩子依次接起来，然后跳到下一层的头继续。

拿示例走一遍：根 $1$ 的孩子是 $2$、$3$，$2$ 下面挂 $4$、$5$，$3$ 只有右孩子 $7$。第一层只有 $1$，把 $2$、$3$ 接上；第二层沿 `2→3` 走，依次接上 $4$、$5$，到 $3$ 时左孩子为空就跳过，再接上 $7$，得到 `4→5→7`。

LC 116 假定每层都满、每个节点必有两个孩子，这里不成立，所以必须跳过空孩子。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
n4, n5, n7 = Node(4), Node(5), Node(7)
n2, n3 = Node(2, n4, n5), Node(3, None, n7)
n1 = Node(1, n2, n3)
connect(n1)
assert n1.next is None
assert n2.next is n3 and n3.next is None
assert n4.next is n5 and n5.next is n7 and n7.next is None
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$。利用已建好的 `next` 时额外空间 $O(1)$；层序队列最坏 $O(n)$。

## 边界

空树返回 `None`。缺左孩子或缺右孩子时，哑节点串下一层要跳过空孩子。底层不连续、中间有空时，靠当前层的 `next` 跳到右侧第一个有孩子的节点，不要假设 `next.left` 一定存在。

## 追问

**如果是完美二叉树（LC 116）呢？**
每层都满、每个节点都有两个孩子，就不用哑节点。对当前节点，`left.next = right`；如果它还有 `next`，再让 `right.next = next.left`。一层用 `next` 走完后，下沉到 `node.left`。时间 $O(n)$，额外空间 $O(1)$。本题孩子可能缺失，这个写法会空指针。

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

**为什么不用父指针？**
当前层已经用 `next` 串成了链表，顺着走一遍就能按从左到右的顺序碰到下一层所有孩子，它本身就相当于「这一层的父节点序列」。哑节点后面的 `tail` 专门负责接孩子，走到层尾自然停下。父指针不会更快，还要改节点结构。
