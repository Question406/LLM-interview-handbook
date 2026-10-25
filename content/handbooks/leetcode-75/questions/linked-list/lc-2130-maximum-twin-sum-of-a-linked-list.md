---
id: lc-2130-maximum-twin-sum-of-a-linked-list
section: linked-list
order: 4
level: A
title: LC 2130 · 链表最大孪生和
quick: >-
  单链表不能倒着走，所以用快慢指针找到后半段起点，原地反转后半段，再和前半段并排走，逐对求和取最大。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2130. Maximum Twin Sum of a Linked List
    url: https://leetcode.com/problems/maximum-twin-sum-of-a-linked-list/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定偶数长度为 n 的单链表，下标从 0 开始。位置 i 与位置 n-1-i 的两个节点互为孪生，考虑 i 从 0 到 n/2-1 的所有配对。每对的孪生和等于两个节点值之和，返回其中最大的和。

### 接口与输出

实现 `pairSum(head: Optional[ListNode]) -> int`。返回最大孪生和，不是节点或下标；每一对按原链表中的位置定义。

### 合法输入与约束

节点数为 2 到 100000 之间的偶数，`1 <= Node.val <= 100000`。示例数组表示从头到尾的节点值，实际参数为链表头节点。

### 示例

```text
输入：head = [5,4,2,1]
输出：6
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/maximum-twin-sum-of-a-linked-list/description/)。

## 解题思路与参考答案

## 题意

链表长度 $n$ 为偶数（$2 \le n \le 10^5$），下标 $i$ 与 $n-1-i$ 的节点互为孪生，孪生和是两者值之和。返回所有孪生和中的最大值。

## 思路

我会把后半段原地反转，再和前半段并排走。孪生对是「第 $i$ 个和倒数第 $i$ 个」，单链表不能倒着走，反转之后后半段的第 $i$ 个就是原来的倒数第 $i$ 个。

找后半段起点用快慢指针，`slow`、`fast` 都从头起跑，`fast` 走到头时 `slow` 停在下标 $n/2$，即后半段起点。反转 `slow` 开头的这段，再用两个指针并排走 $n/2$ 步求最大和。

拿 `[5, 4, 2, 1]` 走一遍。快慢指针走两轮，`slow` 停在下标 2 的节点 2 上。把 `2 → 1` 反转成 `1 → 2`，然后并排走，$5+1=6$，$4+2=6$，答案 6。

最省事的写法是把值倒进数组，再用 `arr[i] + arr[n-1-i]`，额外空间 $O(n)$。面试官要 $O(1)$ 空间时就用反转；如果还要求不改原链表，最后再把后半段反转回去接上。

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


def pairSum(head: Optional[ListNode]) -> int:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    prev = None
    while slow:
        nxt = slow.next
        slow.next = prev
        prev = slow
        slow = nxt
    best = 0
    a, b = head, prev
    while b:
        best = max(best, a.val + b.val)
        a = a.next
        b = b.next
    return best


if __name__ == "__main__":
    assert pairSum(from_list([5, 4, 2, 1])) == 6
    assert pairSum(from_list([4, 2, 2, 3])) == 7
    assert pairSum(from_list([1, 100000])) == 100001
    assert pairSum(from_list([1, 1, 1, 1, 1, 1])) == 2
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert pairSum(from_list([5, 4, 2, 1])) == 6
assert pairSum(from_list([4, 2, 2, 3])) == 7
assert pairSum(from_list([1, 100000])) == 100001
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

$n=2$ 时 `slow` 停在第二个节点，反转后只有一对。

反转后前半段的尾仍指向原后半段第一个节点，这个节点现在是反转段的尾。并排走时以 `b` 为空作终止条件，就不会多算。

节点值都是正数，`best` 从 $0$ 起没问题；允许负数的话要从 $-\infty$ 起。

## 追问

**不允许修改链表呢？**
可以用栈。先把前半段值压栈，再走后半段逐个弹栈配对，额外空间 $O(n)$。也可以照常反转，算完再把后半段反转一次恢复原状，仍是 $O(1)$ 空间。

```python
def pairSumStack(head):
    slow = fast = head
    stack = []
    while fast and fast.next:
        stack.append(slow.val)
        slow = slow.next
        fast = fast.next.next
    best = 0
    while slow:
        best = max(best, stack.pop() + slow.val)
        slow = slow.next
    return best
```

**判断回文链表（LC 234）怎么做？**
同一个骨架，找中点、反转后半段、并排比较值是否相等。奇数长度时中间节点落在后半段起点，反转后它是后半段的尾，前半段先走完就结束，不影响判断。反转写法见 `lc-206-reverse-linked-list`。
