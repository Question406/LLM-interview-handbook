---
id: lc-25-reverse-nodes-in-k-group
section: linked-list
order: 6
level: S
title: LC 25 · K 个一组翻转链表
quick: "从哑结点出发，每次先数够 $k$ 个节点，再把这一段反转后接回去；数不够 $k$ 个就保持原序结束。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Linked List
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 25. K 个一组翻转链表
    url: https://leetcode.cn/problems/reverse-nodes-in-k-group/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定单链表和正整数 k，将节点从头开始每 k 个分为一组，逐组颠倒节点的连接顺序。最后剩余节点如果不足 k 个，必须保持原来的顺序。不同组之间仍按原先的组顺序连接。

### 输入与输出

实现 `reverseKGroup(head, k) -> ListNode`，返回修改后链表的头节点。只能调整节点连接，不能通过修改节点值完成翻转。示例数组按 next 链从头到尾列出节点值。

### 约束与约定

- 链表有 n 个节点，`1 <= k <= n <= 5000`。
- `0 <= Node.val <= 1000`。
- 进阶要求只使用常数额外空间。

### 示例

```text
输入：head = [1,2,3,4,5], k = 2
输出：[2,1,4,3,5]
```

示例前两组 [1,2]、[3,4] 各自翻转，最后的节点 5 不足一组，保持不动。

[官方原题与完整题面](https://leetcode.com/problems/reverse-nodes-in-k-group/description/)。

## 解题思路与参考答案

## 题意

链表每 $k$ 个节点一组翻转，最后不足 $k$ 个的保持原顺序。只能改指针，不能改节点的值。

## 思路

我按「先数后翻，不够不翻」来做，每组单独反转再接回原链。哑结点 `dummy` 当第一组的前驱。每次从当前组的前驱出发数 $k$ 步，数不到就结束；数到了，就把这一段按 206 的方式反转。反转时把这一段之后的节点当成「空」，这样反转完，段尾会自动接上剩下的链表。然后把前驱接到新头，这一组的新尾就成了下一组的前驱。

拿 `[1, 2, 3, 4, 5]`、$k=2$ 走一遍。先数到 2，翻成 2、1，1 后面接着 3；再以 1 为前驱数到 4，翻成 4、3；最后只剩一个 5，数不够两个，原样留着，结果是 `[2, 1, 4, 3, 5]`。

别先整表反转再切。

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


def reverseKGroup(head: Optional[ListNode], k: int) -> Optional[ListNode]:
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


if __name__ == "__main__":
    assert to_list(reverseKGroup(from_list([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
    assert to_list(reverseKGroup(from_list([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
    assert to_list(reverseKGroup(from_list([1]), 1)) == [1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(reverseKGroup(from_list([1, 2, 3, 4, 5]), 2)) == [2, 1, 4, 3, 5]
assert to_list(reverseKGroup(from_list([1, 2, 3, 4, 5]), 3)) == [3, 2, 1, 4, 5]
assert to_list(reverseKGroup(from_list([1]), 1)) == [1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，每个节点最多被数一次、反转一次。额外空间 $O(1)$。

## 边界

- $k=1$ 时每组只有一个节点，反转等于没动，原表不变。
- $n$ 恰好整除 $k$ 时，最后一组也要翻，没有剩余。
- 最后一组不足 $k$ 个时，数不到 $k$ 个就直接返回，保持原序。
- 整表长度小于 $k$ 时，第一次就返回原来的头。

## 追问

**两两交换（LC 24）怎么写？**
就是 $k=2$ 的特例，不用通用地数 $k$ 步。哑结点 `pred`，每次取 `a=pred.next`、`b=a.next`，接成 `pred -> b -> a -> 后续`，再让 `pred=a` 处理下一对。长度为奇数时，最后一个保持不动。时间 $O(n)$，额外空间 $O(1)$。递归写法是 `head.next` 接 `swapPairs(head.next.next)`，再把 `head` 接到后面，栈 $O(n)$，面试默认写迭代。

```python
def swapPairs(head):
    dummy = ListNode(0, head)
    pred = dummy
    while pred.next and pred.next.next:
        a = pred.next
        b = a.next
        pred.next, a.next, b.next = b, b.next, a
        pred = a
    return dummy.next
```

**要从后往前按 $k$ 个一组翻呢？**
先求长度 $n$，跳过前 $n \bmod k$ 个不翻，对剩下的后缀跑这题。也可以先整表反转、再按组翻、再整表反转回来，三次都是 $O(n)$。第一种少一次整表反转，指针更直观。$n \bmod k=0$ 时，结果和从前往后一样。先按组翻再整体反转，得到的分组没有从尾对齐，别这么写。

```python
def reverseKGroupFromEnd(head, k):
    n, cur = 0, head
    while cur:
        n += 1
        cur = cur.next
    skip = n % k
    dummy = ListNode(0, head)
    pred = dummy
    for _ in range(skip):
        pred = pred.next
    pred.next = reverseKGroup(pred.next, k)
    return dummy.next
```
