---
id: lc-328-odd-even-linked-list
section: linked-list
order: 2
level: A
title: LC 328 · 奇偶链表
quick: >-
  题目要 $O(1)$ 额外空间，所以原地拆成两条链交替挂：`odd` 接奇数位，`even` 接偶数位，记住偶链头，最后把奇链尾接到偶链头。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 328. Odd Even Linked List
    url: 'https://leetcode.com/problems/odd-even-linked-list/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定单链表，把原先处在第 1、3、5……个位置的节点排在前面，再接上原先处在第 2、4、6……个位置的节点。两组内部都必须保留原有的相对顺序。奇偶判断依据节点位置，不依据节点值。

### 输入与输出

实现 `oddEvenList(head) -> ListNode | None`，返回重排后的头节点。使用原节点调整 next 连接，不改变节点值；示例数组按链表从头到尾的顺序列出值。

### 约束与约定

- 节点数在 0 到 10000 之间，空链表返回 None。
- 节点值在 `[-1000000,1000000]`。
- 要求 `O(n)` 时间和 `O(1)` 额外空间。

### 示例

```text
输入：head = [1,2,3,4,5]
输出：[1,3,5,2,4]
```

示例中奇数位置节点的值为 [1,3,5]，偶数位置节点的值为 [2,4]，结果按两组连接。

[官方原题与完整题面](https://leetcode.com/problems/odd-even-linked-list/description/)。

## 解题思路与参考答案

## 题意

单链表，把所有奇数位置（第 $1, 3, 5, \dots$ 个，按位置算，和节点值无关）的节点放到前面，偶数位置放到后面，两组内部保持原相对顺序。要求 $O(1)$ 额外空间、$O(n)$ 时间，返回新头。

## 思路

我会原地拆成奇、偶两条链，最后首尾相接。题目要求 $O(1)$ 额外空间，用额外数组收集再重连能做，但违反这个要求。

`odd` 从头开始，`even` 从第二个开始，另存 `even_head`。每轮先 `odd.next = even.next`，`odd` 前进；再 `even.next = odd.next`，`even` 前进。循环条件是 `even and even.next`，意思是偶链指针后面还有下一个奇数节点可以挂。结束后 `odd` 停在奇链尾，接上 `even_head`。

拿 `1 → 2 → 3 → 4 → 5` 走一遍。第一轮 1 接 3、2 接 4；第二轮 3 接 5、4 接 `None`，`even` 变空，循环结束。`odd` 停在 5，接上偶链头 2，得到 `1 → 3 → 5 → 2 → 4`。

偶链尾在最后一步会被置成 `odd.next`，这时奇链已经走完，值是 `None`，所以不会成环。

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


def oddEvenList(head: Optional[ListNode]) -> Optional[ListNode]:
    if head is None:
        return None
    odd, even = head, head.next
    even_head = even
    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return head


if __name__ == "__main__":
    assert to_list(oddEvenList(from_list([1, 2, 3, 4, 5]))) == [1, 3, 5, 2, 4]
    assert to_list(oddEvenList(from_list([2, 1, 3, 5, 6, 4, 7]))) == [
        2,
        3,
        6,
        7,
        1,
        5,
        4,
    ]
    assert to_list(oddEvenList(from_list([]))) == []
    assert to_list(oddEvenList(from_list([1]))) == [1]
    assert to_list(oddEvenList(from_list([1, 2]))) == [1, 2]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(oddEvenList(from_list([1, 2, 3, 4, 5]))) == [1, 3, 5, 2, 4]
assert to_list(oddEvenList(from_list([2, 1, 3, 5, 6, 4, 7]))) == [2, 3, 6, 7, 1, 5, 4]
assert to_list(oddEvenList(from_list([]))) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

空链表或单节点直接返回。

两个节点时循环一次都不进，`odd.next` 重新接回偶链头，链表原样不变。

偶数长度时 `even` 走到尾节点停，奇数长度时 `even` 变成 `None` 停，两种都不会成环。

## 追问

**改成按值的奇偶分组呢？**
同样拆两条链，但要用两个哑结点，因为第一个奇数值未必是头。遍历时按 `val % 2` 挂到对应链尾，最后奇链尾接偶链头、偶链尾置 `None`。这就是 LC 86 分隔链表的套路。

```python
def partitionByParity(head):
    odd_dummy, even_dummy = ListNode(), ListNode()
    o, e = odd_dummy, even_dummy
    while head:
        if head.val % 2:
            o.next = head
            o = o.next
        else:
            e.next = head
            e = e.next
        head = head.next
    e.next = None
    o.next = even_dummy.next
    return odd_dummy.next
```

**为什么循环条件是 `even and even.next`？**
因为每轮要读 `even.next` 作为下一个奇数节点，`even` 本身不能为空；`even.next` 为空说明奇数节点已经用完，再走就会把 `odd` 推到 `None`，最后一步 `odd.next = even_head` 会报错。
