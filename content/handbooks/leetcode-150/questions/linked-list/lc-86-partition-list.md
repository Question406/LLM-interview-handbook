---
id: lc-86-partition-list
section: linked-list
order: 10
level: A
title: LC 86 · 分隔链表
quick: >-
  小于 $x$ 的节点接到一条链，其余的接到另一条，各自保持原来的顺序，最后把左链尾接到右链头。右链尾巴一定要置空，时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 86. 分隔链表
    url: 'https://leetcode.cn/problems/partition-list/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定单链表头节点 head 和整数 x，重新排列链表，使所有值小于 x 的节点排在所有值大于或等于 x 的节点之前。两个分组内部都必须保持节点在原链表中的相对顺序。

### 接口与输出

实现 `partition(head: Optional[ListNode], x: int) -> Optional[ListNode]`，返回重排后的头节点。保留所有节点值及其出现次数；等于 x 的节点属于后一组。

### 合法输入与约束

节点数为 0 到 200，`-100 <= Node.val <= 100`，`-200 <= x <= 200`。空链表合法，不能把这个任务理解成对整条链表排序。

### 示例

```text
输入：head = [1,4,3,2,5,2], x = 3
输出：[1,2,2,4,3,5]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/partition-list/description/)。

## 解题思路与参考答案

## 题意

重排链表，让所有小于 $x$ 的节点都排在大于等于 $x$ 的节点前面，两类内部的相对顺序不变。例如 `1,4,3,2,5,2` 且 $x=3$ 得到 `1,2,2,4,3,5`。

## 思路

我用两条哑链分别收两类节点，最后拼起来，这样相对顺序自然保持不变。`left` 收小于 $x$ 的，`right` 收其余的，按原顺序扫描，把节点原样接到对应链的尾巴上。扫完先把 `right` 的尾巴置空，否则可能成环，再把 `left` 的尾巴接到 `right` 的头。

拿 `1,4,3,2,5,2`、$x=3$ 走一遍。左链依次收到 1、2、2，右链收到 4、3、5，拼起来就是 `1,2,2,4,3,5`。

题目要求稳定顺序，只交换节点值做不到这一点，题目也允许改指针，所以直接拆链。白板上我会先画两条链再拼接。

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


def partition(head: Optional[ListNode], x: int) -> Optional[ListNode]:
    left_d = ListNode()
    right_d = ListNode()
    left, right = left_d, right_d
    while head:
        if head.val < x:
            left.next = head
            left = left.next
        else:
            right.next = head
            right = right.next
        head = head.next
    right.next = None
    left.next = right_d.next
    return left_d.next


if __name__ == "__main__":
    assert to_list(partition(from_list([1, 4, 3, 2, 5, 2]), 3)) == [1, 2, 2, 4, 3, 5]
    assert to_list(partition(from_list([2, 1]), 2)) == [1, 2]
    assert to_list(partition(from_list([1]), 0)) == [1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(partition(from_list([1, 4, 3, 2, 5, 2]), 3)) == [1, 2, 2, 4, 3, 5]
assert to_list(partition(from_list([2, 1]), 2)) == [1, 2]
assert to_list(partition(from_list([1]), 0)) == [1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个节点改一次 `next`。

## Edge Cases

- 全部小于 $x$ 时右链为空，`left` 接到 `None`，相对顺序不变。
- 全部不小于 $x$ 时左链为空，返回右链的头。
- $x$ 比所有值都小时，全部进右链。
- 单节点时进其中一条，另一条为空。

## 追问

**为什么右链尾巴一定要置空？**
因为右链最后一个结点原来的 `next` 可能指向一个已经分到左链的结点，不 `right.next = None` 的话，拼接后会从右尾绕回左链，形成环。左尾接下来马上要接到右头，所以左尾不用提前置空。右链为空时 `right` 还是哑结点，置空就是 `dummy.next = None`，没有坏处。我会拿 `1,4,3,2` 且 $x=3$ 画一下，`4` 的旧后继是 `3`，右链尾巴 `3` 的旧后继是 `2`，而 `2` 已经被接到左边了。

```python
# 扫完必须：
right.next = None
left.next = right_d.next
```

**数组版的稳定划分怎么写？**
开两个数组分别收 $\lt x$ 和 $\ge x$ 的元素，再拼接，稳定而且 $O(n)$。从两端双指针交换就不稳定了，右边一个小的被换到左边时，越过了中间的元素。原地稳定划分要用块交换或者额外 $O(n)$ 的缓冲，面试不用硬写。链表这题本身就是稳定的 $O(1)$ 额外空间，这是链表比数组好写的地方。

```python
def partitionArray(nums, x):
    left = [v for v in nums if v < x]
    right = [v for v in nums if v >= x]
    return left + right
```
