---
id: lc-141-linked-list-cycle
section: linked-list
order: 1
level: S
title: LC 141 · 环形链表
quick: 用 Floyd 快慢指针，慢的一次走一步、快的一次走两步，相遇就说明有环，快指针走到空就没环。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Linked List
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 141. 环形链表
    url: 'https://leetcode.cn/problems/linked-list-cycle/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定单链表头节点 head，判断沿 next 指针不断前进时，是否会再次访问同一个节点对象。如果会，则链表中存在环；如果最终到达 None，则没有环。节点值重复本身不代表存在环。

### 接口与输出

实现 `hasCycle(head: Optional[ListNode]) -> bool`。ListNode 具有 val 和 next 字段。示例里的 pos 仅用于构造数据：把末节点的 next 指向下标为 pos 的节点，pos=-1 表示不连接成环；pos 不是 hasCycle 的参数。

### 合法输入与约束

节点数为 0 到 10000，`-100000 <= Node.val <= 100000`；pos 为 -1 或合法节点下标。空链表也属于合法输入。

### 示例

```text
输入：head = [3,2,0,-4], pos = 1
输出：true
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/linked-list-cycle/description/)。

## 解题思路与参考答案

## 题意

给链表的头节点，判断链表里有没有环，也就是某个节点的 `next` 会再次指回前面的节点。有环返回 `true`，否则返回 `false`。

## 思路

我用 Floyd 判环，因为它只要两个指针，不占额外空间。`slow` 每次走一步，`fast` 每次走两步。有环的时候两个指针最后都在环里转，快的每步追近一格，一定会相遇；没环的话 `fast` 会先走到空。

拿样例 `[3, 2, 0, -4]`、`pos=1` 走一遍，尾巴 `-4` 接回 `2`。第一步 `slow` 在 2、`fast` 在 0；第二步 `slow` 在 0，`fast` 绕回 2；第三步 `slow` 到 -4，`fast` 也到 -4，相遇，返回 `true`。

用哈希记访问过的节点也能判，代价是 $O(n)$ 的空间。开口我会先讲「相对速度为 $1$，环上必相遇」，再写循环条件 `fast and fast.next`。

## 参考代码

```python
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


def from_list(vals: List[int], pos: int = -1) -> Optional[ListNode]:
    dummy = ListNode()
    cur = dummy
    nodes: List[ListNode] = []
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
        nodes.append(cur)
    if pos >= 0:
        cur.next = nodes[pos]
    return dummy.next


def hasCycle(head: Optional[ListNode]) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


if __name__ == "__main__":
    assert hasCycle(from_list([3, 2, 0, -4], 1)) is True
    assert hasCycle(from_list([1, 2], 0)) is True
    assert hasCycle(from_list([1], -1)) is False
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
assert hasCycle(from_list([3, 2, 0, -4], 1)) is True
assert hasCycle(from_list([1, 2], 0)) is True
assert hasCycle(from_list([1], -1)) is False
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。无环时扫一遍；有环时快慢在环内相遇，圈数不超过环长。

## Edge Cases

- 空表或者单节点无环时，`fast` 或 `fast.next` 为空，返回假。
- 自环（`pos=0`）时，第一步 `slow` 和 `fast` 都回到头，马上相遇。
- 环挂在尾巴上、入口在中间时，相遇点一般不是入口。
- 两个节点互相指向时，第一步之后就相遇。

## 追问

**环的入口在哪（LC 142）？**
Floyd 相遇之后别停，再走一轮就能找到。设头到入口 $a$ 步、入口到相遇点 $b$ 步、环长 $c$。慢指针走了 $a+b$，快指针走了 $a+b+kc=2(a+b)$，所以 $a=kc-b$，也就是「从头走 $a$ 步」和「从相遇点再走 $a$ 步」会同时到达入口。于是把一个指针放回头，两个指针每次各走一步，再次相遇的地方就是入口。无环返回 `None`。时间 $O(n)$，额外空间 $O(1)$。别把相遇点当成入口。

```python
def detectCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            p = head
            while p is not slow:
                p = p.next
                slow = slow.next
            return p
    return None
```

**为什么快慢指针一定会相遇，不会跳过去？**
因为相对速度是 $1$，快指针每次只比慢指针多走一格。无环时快指针先到空，正确返回假。有环时两者进环之后，环上的距离每步缩短 $1$，模 $c$ 意义下一定会减到 $0$。节点是离散的，快走两步、慢走一步，相对位移恰好是 $1$，不存在「跨过慢指针」的情况。哈希记访问过的节点也能判环，但要 $O(n)$ 空间，面试默认写 Floyd。

```python
def hasCycleHash(head):
    seen = set()
    while head:
        if head in seen:
            return True
        seen.add(head)
        head = head.next
    return False
```
