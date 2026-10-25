---
id: lc-23-merge-k-sorted-lists
section: divide-conquer
order: 4
level: S
title: LC 23 · 合并 K 个升序链表
quick: "用小根堆存每条链表当前的头结点，每次弹出最小的接到结果上，再把它的后继推进堆，时间 $O(N\\log k)$，$N$ 为总结点数。分治两两归并也是 $O(N\\log k)$；一条条顺序合并会退化成 $O(Nk)$。"
tags:
  - Heap
  - Linked List
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 23. 合并 K 个升序链表
    url: https://leetcode.cn/problems/merge-k-sorted-lists/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定 k 条分别按非递减顺序排列的单链表，把它们的全部节点元素合并为一条非递减链表。不同链表中或同一链表中出现的重复值都需要保留相应次数。

### 输入与输出

实现 `mergeKLists(lists: List[Optional[ListNode]]) -> Optional[ListNode]`，返回合并结果的头节点。输入列表中的某些链表可以为空，k 也可以为 0；没有任何节点时返回 `None`。示例的每个内层列表按头到尾列出一条链表的节点值。

### 约束

- `0 <= k <= 10^4`，每条链表长度为 0 到 500。
- 所有链表的节点总数不超过 `10^4`，节点值在 `[-10^4,10^4]`。
- 每条输入链表都已非递减排序。

### 示例

```text
输入：lists = [[1,4,5],[1,3,4],[2,6]]
输出：[1,1,2,3,4,4,5,6]
```

## 解题思路与参考答案

## 题意

`lists` 里有 $k$ 条升序链表，可能含空表。合并成一条升序链表。

## 思路

我会用小根堆。$k$ 条链表各自有序，下一个最小值一定是某条链表当前的头结点，堆正好能在 $O(\log k)$ 里从这 $k$ 个头里取出最小的。堆里存 `(val, i, node)`，每次弹出最小节点接到结果尾部，再把它的后继入堆。值相同时比较下标 $i$，避免 Python 直接比较节点对象。

以 `[1,4,5]`、`[1,3,4]`、`[2,6]` 为例，堆里一开始是三个头 `1`、`1`、`2`。弹出第一条的 `1`，推进它后面的 `4`；再弹出第二条的 `1`，推进 `3`；接着依次是 `2`、`3`、`4`……一直弹到堆空，得到 `1,1,2,3,4,4,5,6`。

另一种写法是分治：相邻两条按 LC 21 合并，按区间递归，层数 $\log k$，同样是 $O(N\log k)$。拿已合并的结果循环 $k-1$ 次、和下一条两两扫，是 $O(Nk)$，别这么写。白板上先写堆，分治口头补一句，代码放在追问里。

## 参考代码

```python
import heapq
from typing import List, Optional


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def mergeKLists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
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


if __name__ == "__main__":
    def from_list(vals):
        dummy = ListNode()
        cur = dummy
        for v in vals:
            cur.next = ListNode(v)
            cur = cur.next
        return dummy.next

    def to_list(head):
        out = []
        while head:
            out.append(head.val)
            head = head.next
        return out

    ans = mergeKLists([from_list([1, 4, 5]), from_list([1, 3, 4]), from_list([2, 6])])
    assert to_list(ans) == [1, 1, 2, 3, 4, 4, 5, 6]
    assert mergeKLists([]) is None
    assert mergeKLists([None]) is None
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
def from_list(vals):
        dummy = ListNode()
        cur = dummy
        for v in vals:
            cur.next = ListNode(v)
            cur = cur.next
        return dummy.next
def to_list(head):
        out = []
        while head:
            out.append(head.val)
            head = head.next
        return out
ans = mergeKLists([from_list([1, 4, 5]), from_list([1, 3, 4]), from_list([2, 6])])
assert to_list(ans) == [1, 1, 2, 3, 4, 4, 5, 6]
assert mergeKLists([]) is None
assert mergeKLists([None]) is None
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

堆的大小至多 $k$，每个结点进出堆各一次，时间 $O(N\log k)$，额外空间 $O(k)$。分治的递归栈是 $O(\log k)$。

## 边界

$k=0$ 或 `lists` 为空时堆是空的，返回 `None`；全是空表时入堆循环全部跳过，同样返回 `None`。只有一条时堆里只有一个头，一路弹出接上就行。某条特别长也没关系，它的结点陆续入堆，堆大小始终 $\le k$，不会退化成 $O(Nk)$。

## 追问

**不用堆，分治两两归并怎么写？**
把 $k$ 条按下标对半切，递归合并左右两组，最底层两条用 LC 21 的哨兵归并。递归树有 $\log k$ 层，每层每个结点只看一次，总时间 $O(N\log k)$，额外栈 $O(\log k)$。顺序循环 `merge(ans, lists[i])` 会让已合并的前缀越来越长，变成 $O(Nk)$，面试时可以主动拿来对比。

```python
def mergeKListsDC(lists):
    if not lists:
        return None

    def merge(a, b):
        dummy = ListNode()
        cur = dummy
        while a and b:
            if a.val <= b.val:
                cur.next, a = a, a.next
            else:
                cur.next, b = b, b.next
            cur = cur.next
        cur.next = a or b
        return dummy.next

    def dc(lo, hi):
        if lo == hi:
            return lists[lo]
        mid = (lo + hi) // 2
        return merge(dc(lo, mid), dc(mid + 1, hi))

    return dc(0, len(lists) - 1)
```

**换成 $k$ 路有序数组合并呢？**
一样用小根堆，存 `(值, 数组下标, 元素下标)`，弹出后把同一数组的下一个元素推进去，时间 $O(N\log k)$。只有两路、而且 `nums1` 尾部留了空位的话，就是 LC 88 的从右往左三指针，独立卡见 `lc-88-merge-sorted-array`。分治两两 `merge` 也可以，要 $O(N)$ 的缓冲。

```python
def mergeKArrays(arrs):
    heap, ans = [], []
    for i, a in enumerate(arrs):
        if a:
            heapq.heappush(heap, (a[0], i, 0))
    while heap:
        v, i, j = heapq.heappop(heap)
        ans.append(v)
        if j + 1 < len(arrs[i]):
            heapq.heappush(heap, (arrs[i][j + 1], i, j + 1))
    return ans
```
