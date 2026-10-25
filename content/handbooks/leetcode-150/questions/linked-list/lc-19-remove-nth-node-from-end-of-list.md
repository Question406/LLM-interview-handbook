---
id: lc-19-remove-nth-node-from-end-of-list
section: linked-list
order: 7
level: S
title: LC 19 · 删除链表的倒数第 N 个结点
quick: "用哑结点加快慢指针，快指针先走 $n$ 步，然后两个一起走，快指针到末尾时，慢指针正好停在待删结点的前驱。一遍扫完，时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Linked List
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 19. 删除链表的倒数第 N 个结点
    url: https://leetcode.cn/problems/remove-nth-node-from-end-of-list/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定无环单链表头节点 `head` 和正整数 n，删除从链表末尾往前数的第 n 个节点，并返回删除后的头节点。倒数第 1 个节点就是尾节点；如果删除的是原头节点，返回值需要指向新的头。

### 输入与输出

实现 `removeNthFromEnd(head, n) -> ListNode | None`。直接调整原链表的连接，其他节点的相对顺序和节点值不变。示例数组只表示节点值；删除唯一节点后得到空链表，接口返回 None。

### 约束

- 设链表长度为 sz，`1 <= sz <= 30`。
- `0 <= Node.val <= 100`。
- `1 <= n <= sz`，保证要删除的节点存在。

### 示例

```text
输入：head = [1,2,3,4,5], n = 2
输出：[1,2,3,5]
```

[LeetCode 原题](https://leetcode.com/problems/remove-nth-node-from-end-of-list/description/)

## 解题思路与参考答案

## 题意

删除单链表的倒数第 $n$ 个结点，返回头结点。题目保证 $n$ 合法。

## 思路

我用快慢指针一遍扫完，先求长度再走 `len-n` 步要扫两遍。加一个哑结点，快指针先走 $n$ 步，然后快慢同步往前走。当 `fast.next` 为空时，`slow` 正好是待删结点的前驱，执行 `slow.next = slow.next.next` 就删掉了。

拿 `[1, 2, 3, 4, 5]`、$n=2$ 走一遍。快指针从哑结点先走两步到 2，然后两个一起走，快指针走到 5 时慢指针停在 3，删掉 3 的后继 4，得到 `[1, 2, 3, 5]`。

有了哑结点，删头的时候也不用特判。白板上我会先画出「快慢间距为 $n$」。

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


def removeNthFromEnd(head: Optional[ListNode], n: int) -> Optional[ListNode]:
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next
    while fast.next:
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next
    return dummy.next


if __name__ == "__main__":
    assert to_list(removeNthFromEnd(from_list([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
    assert to_list(removeNthFromEnd(from_list([1]), 1)) == []
    assert to_list(removeNthFromEnd(from_list([1, 2]), 1)) == [1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(removeNthFromEnd(from_list([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
assert to_list(removeNthFromEnd(from_list([1]), 1)) == []
assert to_list(removeNthFromEnd(from_list([1, 2]), 1)) == [1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。快指针走完全表一次。

## 边界

- 删头（$n$ 等于链长）时，哑结点让 `slow` 停在 dummy，`dummy.next` 跳过原来的头。
- 删尾（$n=1$）时，快指针先走 $1$ 步到原头，同步之后 `slow` 停在倒数第二个。
- 只剩一个节点时，删的既是头也是尾，返回空。
- 题目保证 $n$ 合法，不用处理 $n$ 过大的情况。

## 追问

**只要找到倒数第 $k$ 个节点、不删呢？**
快指针从 `head` 出发先走 $k$ 步，不用哑结点，然后快慢同步，快指针走到空时，慢指针就是目标。间距还是 $k$，只是少了一次前驱操作。$k$ 等于链长时，快指针先走完，慢指针还在头，结果也对。时间 $O(n)$，额外空间 $O(1)$。先求长度再走 `len-k` 也行，只是要两遍。

```python
def kthFromEnd(head, k):
    fast = slow = head
    for _ in range(k):
        fast = fast.next
    while fast:
        fast = fast.next
        slow = slow.next
    return slow
```

**换成双向链表或者数组呢？**
数组有下标，倒数第 $n$ 个就是 `arr[len(arr)-n]`，删的话 `pop` 或者切片。双向链表有尾指针时，从尾巴走 $n-1$ 步到目标，再改 `prev/next`。单链表既没有前驱也没有下标，所以才要「快慢间距为 $n$」这一招。三种结构的代价各不一样，数组 $O(1)$ 定位、$O(n)$ 删除，双链 $O(n)$ 定位、$O(1)$ 删除，单链定位和删除都是 $O(n)$，但一遍就扫完了。
