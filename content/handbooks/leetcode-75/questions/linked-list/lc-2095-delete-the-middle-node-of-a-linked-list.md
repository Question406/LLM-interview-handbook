---
id: lc-2095-delete-the-middle-node-of-a-linked-list
section: linked-list
order: 1
level: A
title: LC 2095 · 删除链表的中间节点
quick: >-
  删单链表节点要拿到前驱，所以用快慢指针让慢指针停在中间节点的前驱：`slow=head`、`fast=head.next.next` 起跑，快的走到头时 `slow.next` 就是中间节点，直接跳过它。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2095. Delete the Middle Node of a Linked List
    url: https://leetcode.com/problems/delete-the-middle-node-of-a-linked-list/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定一条非空单链表，删除它的中间节点，并返回删除后的头节点。若链表长度为 n，下标从 0 开始，中间节点定义为下标 floor(n/2) 的节点；因此偶数长度时删除两个中点中靠后的那个。

### 输入与输出

实现 `deleteMiddle(head: Optional[ListNode]) -> Optional[ListNode]`。只删除这一个节点，其余节点的值与相对顺序不变。只有一个节点时，删除后返回 `None`。示例列表从头到尾表示节点值。

### 约束

- 节点数在 1 到 `10^5`。
- 节点值在 1 到 `10^5`，输入为无环单链表。

### 示例

```text
输入：head = [1,3,4,7,1,2,6]
输出：[1,3,4,1,2,6]
```

示例长度为 7，要删除下标 3、值为 7 的节点。

## 解题思路与参考答案

## 题意

长度为 $n$ 的单链表，删除下标为 $\lfloor n/2 \rfloor$ 的节点（下标从 $0$ 计），返回头节点。$n=1$ 时删完为空链表。偶数长度删的是靠后那个中点，例如 $n=4$ 删下标 $2$。

## 思路

我会用快慢指针，让 `slow` 直接停在中间节点的前驱，因为删单链表节点得先拿到前驱。`fast` 比 `slow` 先走两步起跑，之后 `slow` 每走一步 `fast` 走两步，`fast` 走到尾时 `slow` 恰好停在下标 $\lfloor n/2 \rfloor - 1$，执行 `slow.next = slow.next.next` 就删掉了。

拿 `[1, 3, 4, 7, 1, 2, 6]` 走一遍，$n=7$，要删下标 3 的 7。`slow` 在下标 0，`fast` 在下标 2；走一轮到 1 和 4，再走一轮到 2 和 6，这时 `fast.next` 为空，停下。`slow` 在值为 4 的节点上，跳过它后面的 7，得到 `[1, 3, 4, 1, 2, 6]`。

朴素做法是先数长度，再走 $\lfloor n/2 \rfloor - 1$ 步，也是 $O(n)$，只是扫两遍。面试里我会先写两遍扫描把下标说清楚，再换成快慢指针。

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


def deleteMiddle(head: Optional[ListNode]) -> Optional[ListNode]:
    if head is None or head.next is None:
        return None
    slow, fast = head, head.next.next
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    slow.next = slow.next.next
    return head


if __name__ == "__main__":
    assert to_list(deleteMiddle(from_list([1, 3, 4, 7, 1, 2, 6]))) == [1, 3, 4, 1, 2, 6]
    assert to_list(deleteMiddle(from_list([1, 2, 3, 4]))) == [1, 2, 4]
    assert to_list(deleteMiddle(from_list([2, 1]))) == [2]
    assert to_list(deleteMiddle(from_list([1]))) == []
    assert to_list(deleteMiddle(from_list([1, 2, 3]))) == [1, 3]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(deleteMiddle(from_list([1, 3, 4, 7, 1, 2, 6]))) == [1, 3, 4, 1, 2, 6]
assert to_list(deleteMiddle(from_list([1, 2, 3, 4]))) == [1, 2, 4]
assert to_list(deleteMiddle(from_list([2, 1]))) == [2]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

$n=1$ 没有前驱，单独返回 `None`。

$n=2$ 时 `fast` 起跑就是 `None`，`slow` 停在头，删掉第二个节点。

偶数长度删的是靠后的中点，起跑差两步正好对齐这个下标。

## 追问

**要返回中间节点（LC 876）呢？**
`slow`、`fast` 都从 `head` 起跑，`fast` 走到头时 `slow` 就是中点，偶数长度落在靠后那个。和本题只差起跑位置，想停在前驱就让 `fast` 多走两步。

```python
def middleNode(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

**只给要删的节点、拿不到头（LC 237）怎么办？**
拿不到前驱，就把后继的值拷过来，再删掉后继：`node.val = node.next.val; node.next = node.next.next`。前提是这个节点不是尾节点。这种做法改的是值，节点身份变了，外部如果持有后继的引用会出问题，要跟面试官说明。
