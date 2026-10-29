---
id: lc-21-merge-two-sorted-lists
section: linked-list
order: 3
level: S
title: LC 21 · 合并两个有序链表
quick: 用哑结点加双指针，两条链谁的头小就接谁，一条接完后把另一条剩下的整段挂上。时间 $O(m+n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 21. 合并两个有序链表
    url: 'https://leetcode.cn/problems/merge-two-sorted-lists/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定两条分别按非递减顺序排列的单链表 list1 和 list2，将它们合并成一条仍然非递减的链表。结果中应包含两条输入链表的全部元素，重复值按原出现次数保留。

### 接口与输出

实现 `mergeTwoLists(list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]`，返回合并后的头节点。节点包含 val 与 next；可以调整原节点的 next 连接。

### 合法输入与约束

输入链表允许为空，节点数量在公开约束的 0 到 50 范围内，`-100 <= Node.val <= 100`。示例中的数组只表示从头到尾的节点值，不是函数接收的实际类型。

### 示例

```text
输入：list1 = [1,2,4], list2 = [1,3,4]
输出：[1,1,2,3,4,4]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/merge-two-sorted-lists/description/)。

## 解题思路与参考答案

## 题意

两个升序链表，合并成一条仍然升序的链表。可以直接改原节点的指针，不用新建值节点。

## 思路

我用哑结点加迭代双指针，直接改原节点的指针。`cur` 指向已合并部分的尾巴，每次比较两条链的头，把较小的接到 `cur` 后面并前进。一条走完后，另一条剩下的部分本来就有序，直接整段挂上去。

拿样例 `[1, 2, 4]` 和 `[1, 3, 4]` 走一遍。两个 1 相等，先接 `list1` 的；接着 2 比 1 大，接 `list2` 的 1；然后依次接上 2、3、4，`list1` 先走完，把 `list2` 剩下的 4 挂上，得到 `[1, 1, 2, 3, 4, 4]`。

递归也能写，每次返回较小的头并接到递归结果上，但会多 $O(m+n)$ 的栈，面试默认写迭代。相等时接哪边都行，要稳定就优先 `list1`。

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


def mergeTwoLists(
    list1: Optional[ListNode], list2: Optional[ListNode]
) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    while list1 and list2:
        if list1.val <= list2.val:
            cur.next = list1
            list1 = list1.next
        else:
            cur.next = list2
            list2 = list2.next
        cur = cur.next
    cur.next = list1 or list2
    return dummy.next


if __name__ == "__main__":
    assert to_list(mergeTwoLists(from_list([1, 2, 4]), from_list([1, 3, 4]))) == [
        1,
        1,
        2,
        3,
        4,
        4,
    ]
    assert to_list(mergeTwoLists(from_list([]), from_list([]))) == []
    assert to_list(mergeTwoLists(from_list([]), from_list([0]))) == [0]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(mergeTwoLists(from_list([1, 2, 4]), from_list([1, 3, 4]))) == [
    1,
    1,
    2,
    3,
    4,
    4,
]
assert to_list(mergeTwoLists(from_list([]), from_list([]))) == []
assert to_list(mergeTwoLists(from_list([]), from_list([0]))) == [0]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(m+n)$，额外空间 $O(1)$。每个节点被接一次。

## Edge Cases

- 一条链为空时直接返回另一条，`cur.next = list1 or list2` 已经覆盖了。
- 两条链等长交错时，每次接较小的头，稳定写法优先 `list1`。
- 一条链整体更小时，循环里一直接这一条，最后把另一条整段挂上。
- 两条都空时返回 `None`。

## 追问

**合并 $k$ 条有序链表（LC 23）呢？**
用小根堆，每次弹出最小的头结点，再把它的后继压回去，时间 $O(N\log k)$，$N$ 是总结点数。别循环 $k-1$ 次两两扫，那是 $O(Nk)$。Python 的结点不能比较大小，堆里放 `(val, i, node)`，用下标打破平局。分治也可以，相邻两条按这题合并，层数 $\log k$，复杂度相同。独立卡见 `lc-23-merge-k-sorted-lists`。

```python
import heapq


def mergeKLists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    dummy = ListNode()
    cur = dummy
    while heap:
        _, i, node = heapq.heappop(heap)
        cur.next = node
        cur = cur.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

**数组版（LC 88）怎么合并？**
`nums1` 尾部预留了 $n$ 个空位，就从右往左用三指针填，谁大写谁，这样不会覆盖还没读的元素；从左直接写会盖掉 `nums1` 里还没比较的数。链表没有尾部空位，只能从左接。时间 $O(m+n)$，额外空间 $O(1)$。独立卡见 `lc-88-merge-sorted-array`。

```python
def merge(nums1, m, nums2, n):
    i, j, k = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i -= 1
        else:
            nums1[k] = nums2[j]
            j -= 1
        k -= 1
```
