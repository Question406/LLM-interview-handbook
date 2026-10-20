---
id: lc-82-remove-duplicates-from-sorted-list-ii
section: linked-list
order: 8
level: A
title: LC 82 · 删除排序链表中的重复元素 II
quick: "先加一个哑节点，用前驱检查后面两个节点是否同值。如果相同，就跳过这个值的整段节点；否则前驱向前移动。重复值必须全部删除。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 82. 删除排序链表中的重复元素 II
    url: https://leetcode.cn/problems/remove-duplicates-from-sorted-list-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

已排序链表，删除所有出现次数大于 $1$ 的值，一个都不留。返回新头。例如 `1,2,3,3,4,4,5` 变成 `1,2,5`。

## 思路

和 LC 83 不同：重复值要整段删掉。哑结点 `pred`。若 `pred.next` 与再下一个同值，记下该值，把 `pred.next` 一路跳过所有该值；否则 `pred` 前进一步。

必须用前驱：当前节点自己没法判断「自己是不是重复段的第一个」。开口先对齐：删光，不是去重留一。

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

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个节点检查一次、最多摘一次。

## 边界

- 全重复：整段跳过，返回空。
- 头或尾是重复段：哑结点保证删头；尾段 `pred.next` 一路接到 `None`。
- 没有重复：每次走 `else`，`pred` 前进，原表不变。
- 只有一对重复夹在中间：只跳这一段，两侧相对顺序不变。

## 追问

- **重复值只留一个（LC 83）？** 有序则重复相邻。当前结点与后继同值时跳过后继，不同才前进。不必哑结点，因为头结点即使重复也会留下第一个。时间 $O(n)$，额外空间 $O(1)$。和这题的差别：这题是「出现超过一次的值一个不留」，LC 83 是「去重留一」。别在 LC 83 里用前驱整段删。开口先问清留不留。

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

- **链表无序呢？** 先排序再跑这题或 LC 83，排序破坏相对顺序且链表归并要 $O(n\log n)$。若要保留首次出现顺序：一遍哈希计数，二遍只串计数为 $1$ 的结点（对应这题），或二遍遇到没输出过的值就留下（对应 LC 83）。额外空间 $O(U)$，$U$ 为不同值个数。值域很小可用数组当计数表。别一边走一边删却忘了「后面还可能再出现同一值」。

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
