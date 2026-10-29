---
id: lc-61-rotate-list
section: linked-list
order: 9
level: A
title: LC 61 · 旋转链表
quick: 先求长度 $n$，把 $k$ 对 $n$ 取模；然后尾巴接回头成环，再走到新尾（第 $n-k$ 个节点）断开。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 61. 旋转链表
    url: 'https://leetcode.cn/problems/rotate-list/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定单链表 `head` 和非负整数 k，把链表向右旋转 k 次。一次右旋会把当前尾节点移到头部，其他节点保持先后顺序；旋转次数可以大于链表长度。

### 输入与输出

实现 `rotateRight(head, k) -> ListNode | None`，返回旋转后的头节点，并正确更新原节点之间的 next 连接。空链表仍返回 None，k=0 时链表不变；不能把结果留成环。

### 约束

- 节点数在 0 到 500 之间，链表无环。
- `-100 <= Node.val <= 100`。
- `0 <= k <= 2 * 10^9`。
- 示例中的列表按从头到尾的顺序展示节点值。

### 示例

```text
输入：head = [1,2,3,4,5], k = 2
输出：[4,5,1,2,3]
```

[LeetCode 原题](https://leetcode.com/problems/rotate-list/description/)

## 解题思路与参考答案

## 题意

把链表向右旋转 $k$ 位，每个节点往后挪，原来的尾巴接到原来的头前面。例如 `1,2,3,4,5` 且 $k=2$ 得到 `4,5,1,2,3`。

## 思路

我先成环再断开。右旋 $k$ 位等于把后 $k$ 个节点整段搬到前面，成环之后只要断开一个指针。空表、单节点或 $k=0$ 直接返回。扫一遍拿到长度 $n$ 和尾指针，令 $k \bmod n$，结果为 $0$ 就不用动。否则把尾节点接到头上形成环；新尾是原链表的第 $n-k$ 个节点，新头是它的后继，把新尾的 `next` 置空就断开了。

拿 `1,2,3,4,5`、$k=2$ 走一遍。$n=5$，取模后还是 2；5 接回 1 成环，新尾是第 3 个节点 3，新头是 4，断开后得到 `4,5,1,2,3`。

这样写指针改得少，不容易把链弄断。

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


def rotateRight(head: Optional[ListNode], k: int) -> Optional[ListNode]:
    if head is None or head.next is None or k == 0:
        return head
    n = 1
    tail = head
    while tail.next:
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    tail.next = head
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    return new_head


if __name__ == "__main__":
    assert to_list(rotateRight(from_list([1, 2, 3, 4, 5]), 2)) == [4, 5, 1, 2, 3]
    assert to_list(rotateRight(from_list([0, 1, 2]), 4)) == [2, 0, 1]
    assert to_list(rotateRight(from_list([1]), 99)) == [1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert to_list(rotateRight(from_list([1, 2, 3, 4, 5]), 2)) == [4, 5, 1, 2, 3]
assert to_list(rotateRight(from_list([0, 1, 2]), 4)) == [2, 0, 1]
assert to_list(rotateRight(from_list([1]), 99)) == [1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。求长一遍，再走 $n-k$ 步。

## Edge Cases

- $k$ 是 $n$ 的倍数时，取模后为 $0$，原表不动。
- $k \gt n$ 时一定要先 $k \bmod n$，否则会走过头。
- 空表或单节点直接返回。
- $k=0$ 时不旋转。成环前先取模，免得白转一圈。

## 追问

**改成左旋 $k$ 呢？**
左旋 $k$ 等于右旋 $n-k$。先 $k \bmod n$，为 $0$ 直接返回，否则调用这题的 `rotateRight(head, n - k)`。也可以成环后走到第 $k$ 个节点当新尾断开，新头是它的后继。时间还是 $O(n)$。别对 $k$ 再取一次反，容易把方向转错。白板上我会先画 `1,2,3,4,5` 左旋 $2$ 得到 `3,4,5,1,2`。

```python
def rotateLeft(head, k):
    if head is None or head.next is None or k == 0:
        return head
    n, tail = 1, head
    while tail.next:
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    return rotateRight(head, n - k)
```

**数组右旋（LC 189）怎么做？**
数组有下标，不用成环，三次反转就行。$k \bmod n$ 之后先整体反转，再反转前 $k$ 个，再反转后 $n-k$ 个。时间 $O(n)$，额外空间 $O(1)$。环状替换也能做到 $O(1)$，但要处理环的个数。链表没有下标，才用「成环再在 $n-k$ 处断开」。独立卡见 `lc-189-rotate-array`。

```python
def rotateArray(nums, k):
    n = len(nums)
    k %= n

    def reverse(lo, hi):
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo += 1
            hi -= 1

    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)
```
