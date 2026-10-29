---
id: lc-2-add-two-numbers
section: linked-list
order: 2
level: S
title: LC 2 · 两数相加
quick: '链表低位在前，正好按位相加、维护进位，任一链表没走完或者进位不为零就继续建节点。时间 $O(\max(m,n))$，额外空间 $O(1)$（不含答案链）。'
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 2. 两数相加
    url: 'https://leetcode.cn/problems/add-two-numbers/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定两条非空单链表，分别表示两个非负整数。每个节点只存一位十进制数字，并且低位在前：头节点是个位，下一节点是十位，依此类推。将这两个整数相加，返回以相同低位在前形式表示和的新链表。

### 输入与输出

实现 `addTwoNumbers(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]`。示例数组按链表头到尾列出节点值，实际接口传入并返回链表节点。两条输入链表长度可以不同，最终进位可能使结果多一个节点。

### 约束

- 每条输入链表含 1 到 100 个节点。
- 节点值为 0 到 9；除整数 0 自身外，两个整数都没有高位前导零。

### 示例

```text
输入：l1 = [2,4,3], l2 = [5,6,4]
输出：[7,0,8]
```

`[2,4,3]` 表示 342，`[5,6,4]` 表示 465，两者之和 807 用 `[7,0,8]` 表示。

## 解题思路与参考答案

## 题意

两个非空链表表示两个非负整数，数位逆序存储，头结点是个位，每个节点只存一位数字。返回它们的和，同样低位在前。

## 思路

我直接模拟竖式加法，因为头结点就是个位，低位已经对齐了。两条链同时往后走，当前位之和加上进位，写下个位、留下十位。一条链走完后另一条继续加；最后如果进位不为零，再补一个节点。

拿样例 `[2, 4, 3]` 加 `[5, 6, 4]`，也就是 342 加 465。个位 2+5=7；十位 4+6=10，写 0 进 1；百位 3+4+1=8，结果是 `[7, 0, 8]`。

别先转成整数，位数可能上百，会溢出。哑结点省掉第一个节点的特判。开口我先说「低位对齐 + 进位」，再写 `while l1 or l2 or carry`。

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


def addTwoNumbers(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    carry = 0
    while l1 or l2 or carry:
        if l1:
            carry += l1.val
            l1 = l1.next
        if l2:
            carry += l2.val
            l2 = l2.next
        cur.next = ListNode(carry % 10)
        cur = cur.next
        carry //= 10
    return dummy.next


if __name__ == "__main__":
    assert to_list(addTwoNumbers(from_list([2, 4, 3]), from_list([5, 6, 4]))) == [
        7,
        0,
        8,
    ]
    assert to_list(addTwoNumbers(from_list([0]), from_list([0]))) == [0]
    assert to_list(
        addTwoNumbers(from_list([9, 9, 9, 9, 9, 9, 9]), from_list([9, 9, 9, 9]))
    ) == [8, 9, 9, 9, 0, 0, 0, 1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(addTwoNumbers(from_list([2, 4, 3]), from_list([5, 6, 4]))) == [7, 0, 8]
assert to_list(addTwoNumbers(from_list([0]), from_list([0]))) == [0]
assert to_list(
    addTwoNumbers(from_list([9, 9, 9, 9, 9, 9, 9]), from_list([9, 9, 9, 9]))
) == [8, 9, 9, 9, 0, 0, 0, 1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\max(m,n))$，额外空间 $O(1)$（不含新链表）。每位最多访问一次。

## Edge Cases

- 一条链更长时，短链走完后继续加长链和进位。
- 全是 $9$ 时，进位一路传到最高位，最后多出一个节点 $1$。
- 两条链都是 `[0]` 时，循环一次写出 $0$，进位清零。
- 题目保证非空；如果放宽成可以为空，就把空链当成 $0$。

## 追问

**如果高位在前（LC 445）呢？**
这时没法直接对齐个位。我会先把两条链反转，当成原题来加，再把结果反转回来。也可以用两个栈依次压入，弹出时从低位开始加，每次把新节点头插到答案前面。反转写法额外空间 $O(1)$（不计答案），栈写法是 $O(m+n)$。反转原表会改动输入，要先确认允不允许。同样别先转成整数，位数太长会溢出。

```python
def reverseList(head):
    prev = None
    while head:
        nxt = head.next
        head.next = prev
        prev = head
        head = nxt
    return prev


def addTwoNumbersHigh(l1, l2):
    return reverseList(addTwoNumbers(reverseList(l1), reverseList(l2)))
```

**数组版怎么写？**
从尾巴对齐，`i, j` 从末尾往前走，当前位加上进位，结果头插，或者先放进列表最后再反转。最后进位不为零时答案会多一位，比如 `[9,9]+[1]` 得到 `[1,0,0]`；两数组等长且没有进位时长度不变。时间 $O(\max(m,n))$。这里也别用字符串转整数。

```python
def addArrays(a, b):
    i, j, carry, out = len(a) - 1, len(b) - 1, 0, []
    while i >= 0 or j >= 0 or carry:
        if i >= 0:
            carry += a[i]
            i -= 1
        if j >= 0:
            carry += b[j]
            j -= 1
        out.append(carry % 10)
        carry //= 10
    out.reverse()
    return out
```
