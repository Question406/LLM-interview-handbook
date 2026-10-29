---
id: lc-82-remove-duplicates-from-sorted-list-ii
section: linked-list
order: 8
level: A
title: LC 82 · 删除排序链表中的重复元素 II
quick: >-
  用一个从哑结点出发的前驱，看它后面两个节点是否同值，同值就把这个值的整段节点都跳过，不同就前驱前进一步。重复的值一个不留，时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 82. 删除排序链表中的重复元素 II
    url: 'https://leetcode.cn/problems/remove-duplicates-from-sorted-list-ii/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一条已按非递减顺序排列的单链表，删除所有出现次数超过一次的值对应的全部节点，只保留在原链表中恰好出现一次的值。保留节点的相对顺序不变。这里不是每个值留一个副本，而是重复值一个也不留。

### 输入与输出

实现 `deleteDuplicates(head: Optional[ListNode]) -> Optional[ListNode]`，返回处理后的头节点。空链表或全部节点都被删除时返回 `None`；示例列表按头到尾表示节点值。

### 约束

- 节点数为 0 到 300，节点值在 `[-100,100]`。
- 输入保证非递减排序。

### 示例

```text
输入：head = [1,2,3,3,4,4,5]
输出：[1,2,5]
```

3 和 4 在原链表中都重复出现，所以对应的四个节点全部删除，剩下 `[1,2,5]`。

## 解题思路与参考答案

## 题意

已排序的链表，删除所有出现次数大于 $1$ 的值，一个都不留，返回新头。例如 `1,2,3,3,4,4,5` 变成 `1,2,5`。

## 思路

我用一个停在哑结点上的前驱指针来删，因为重复值要整段删掉，只有站在这一段前面，才能连第一个一起删掉。`pred` 从哑结点出发，如果 `pred.next` 和它的下一个同值，就记下这个值，把 `pred.next` 一路往后跳，跳过所有等于这个值的节点；否则 `pred` 前进一步。

拿 `1,2,3,3,4,4,5` 走一遍。1 和 2 不同，`pred` 走到 1；2 和 3 不同，走到 2；接着看到 3、3 同值，把两个 3 都跳过，`pred.next` 变成 4；4、4 也同值，再跳过，`pred.next` 变成 5；最后得到 `1,2,5`。

当前节点自己判断不了「我是不是重复段的第一个」，所以要用前驱。开口我会先和面试官对齐，这题是重复的全删光，和 LC 83 的去重留一不一样。

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


def deleteDuplicates(head: Optional[ListNode]) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    pred = dummy
    while pred.next:
        cur = pred.next
        if cur.next and cur.val == cur.next.val:
            val = cur.val
            while pred.next and pred.next.val == val:
                pred.next = pred.next.next
        else:
            pred = pred.next
    return dummy.next


if __name__ == "__main__":
    assert to_list(deleteDuplicates(from_list([1, 2, 3, 3, 4, 4, 5]))) == [1, 2, 5]
    assert to_list(deleteDuplicates(from_list([1, 1, 1, 2, 3]))) == [2, 3]
    assert to_list(deleteDuplicates(from_list([1, 1, 1]))) == []
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(deleteDuplicates(from_list([1, 2, 3, 3, 4, 4, 5]))) == [1, 2, 5]
assert to_list(deleteDuplicates(from_list([1, 1, 1, 2, 3]))) == [2, 3]
assert to_list(deleteDuplicates(from_list([1, 1, 1]))) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个节点检查一次、最多摘一次。

## Edge Cases

- 全部重复时整段跳过，返回空。
- 头或尾是重复段时，哑结点保证能删头；尾段删完，`pred.next` 一路接到 `None`。
- 没有重复时每次都走 `else`，`pred` 前进，原表不变。
- 只有中间夹着一对重复时，只跳这一段，两侧的相对顺序不变。

## 追问

**重复值只留一个（LC 83）呢？**
有序链表里重复值是相邻的，当前结点和后继同值就跳过后继，不同才前进。不用哑结点，因为头结点就算重复，留下的也是第一个。时间 $O(n)$，额外空间 $O(1)$。两题的差别在于，这题出现超过一次的值一个不留，LC 83 是去重留一，所以 LC 83 里别用前驱整段删。面试时先问清楚留不留。

```python
def deleteDuplicatesKeepOne(head):
    cur = head
    while cur and cur.next:
        if cur.val == cur.next.val:
            cur.next = cur.next.next
        else:
            cur = cur.next
    return head
```

**链表无序呢？**
可以先排序再跑这题或 LC 83，但排序会破坏相对顺序，链表归并也要 $O(n\log n)$。如果要保留首次出现的顺序，就先扫一遍做哈希计数，第二遍只串起计数为 $1$ 的结点（对应这题），或者第二遍遇到没输出过的值才留下（对应 LC 83）。额外空间 $O(U)$，$U$ 是不同值的个数；值域很小时可以用数组当计数表。别一边走一边删，后面还可能再出现同一个值。

```python
def deleteAllDupsUnsorted(head):
    cnt = {}
    cur = head
    while cur:
        cnt[cur.val] = cnt.get(cur.val, 0) + 1
        cur = cur.next
    dummy = ListNode(0)
    tail, cur = dummy, head
    while cur:
        if cnt[cur.val] == 1:
            tail.next = cur
            tail = cur
        cur = cur.next
    tail.next = None
    return dummy.next
```
