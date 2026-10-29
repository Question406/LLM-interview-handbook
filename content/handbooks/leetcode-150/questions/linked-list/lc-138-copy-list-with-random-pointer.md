---
id: lc-138-copy-list-with-random-pointer
section: linked-list
order: 4
level: A
title: LC 138 · 随机链表的复制
quick: >-
  用哈希表记「旧节点到新节点」，第一遍按 `next` 建副本，第二遍接 `next` 和 `random`，时间 $O(n)$，哈希空间
  $O(n)$。想省掉哈希，可以三步交织复制，把副本插在原节点后面。
tags:
  - Linked List
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 138. 随机链表的复制
    url: 'https://leetcode.cn/problems/copy-list-with-random-pointer/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一条单链表，每个节点除 next 之外还有 random 指针，random 可以指向本链表中的任意节点，也可以为空。创建这条链表的深拷贝：新节点的值与原节点一一对应，next 和 random 都应指向新链表中的对应对象，不能复用原节点或让新指针指回原链表。

### 输入与输出

实现 `copyRandomList(head: Optional[Node]) -> Optional[Node]`，返回新链表头；空链表返回 `None`。示例用 `[value,randomIndex]` 描述每个节点，列表顺序决定 next，randomIndex 是从 0 开始的原链表下标，`null` 表示 random 为空。实际输入和返回值都是节点对象。

### 约束

- 节点数为 0 到 1000，节点值范围为 `[-10^4,10^4]`。
- 每个 random 都是空指针或指向链表中的一个节点，next 组成普通无环单链表。

### 示例

```text
输入：head = [[7,null],[13,0],[11,4],[10,2],[1,0]]
输出：[[7,null],[13,0],[11,4],[10,2],[1,0]]
```

输入输出的序列表示相同是正确的，但输出必须由全新的节点组成。

## 解题思路与参考答案

## 题意

每个节点除了 `next` 还有一个 `random`，可以指向表中任意节点或者为空。要返回整张表的深拷贝，新节点的值相同，指针都指向新表里对应的节点，不能复用旧节点。

## 思路

我先用哈希表做，因为 `random` 可能指向后面还没建出来的节点，先把所有副本建好再接线最省心。哈希表记「旧节点 $\to$ 新节点」，第一遍只沿 `next` 建副本并登记，第二遍再用哈希给每个新节点接上 `next` 和 `random`。`random` 为空时，`dict.get` 拿到的就是 `None`。

拿样例 `[[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]` 来说，值为 $11$ 的节点 `random` 指向下标 $4$ 的节点，那个节点排在它后面。第一遍结束时所有副本都已经在哈希里了，第二遍直接查出来接上就行。

写完哈希版，我会再提空间优化的做法。在每个旧节点后面插入副本，再按「旧.random 的后继」改副本的 `random`，最后拆成两条链，细节放在追问里讲。

## 参考代码

```python
from typing import List, Optional


class Node:
    def __init__(
        self, x: int, next: Optional["Node"] = None, random: Optional["Node"] = None
    ):
        self.val = int(x)
        self.next = next
        self.random = random


def from_pairs(pairs: List[List[Optional[int]]]) -> Optional[Node]:
    nodes = [Node(v) for v, _ in pairs]
    for i, (_, r) in enumerate(pairs):
        if i + 1 < len(nodes):
            nodes[i].next = nodes[i + 1]
        if r is not None:
            nodes[i].random = nodes[r]
    return nodes[0] if nodes else None


def to_pairs(head: Optional[Node]) -> List[List[Optional[int]]]:
    nodes: List[Node] = []
    cur = head
    while cur:
        nodes.append(cur)
        cur = cur.next
    index = {id(n): i for i, n in enumerate(nodes)}
    return [
        [n.val, index[id(n.random)] if n.random is not None else None] for n in nodes
    ]


def copyRandomList(head: Optional[Node]) -> Optional[Node]:
    if head is None:
        return None
    old_to_new = {}
    cur = head
    while cur:
        old_to_new[cur] = Node(cur.val)
        cur = cur.next
    cur = head
    while cur:
        old_to_new[cur].next = old_to_new.get(cur.next)
        old_to_new[cur].random = old_to_new.get(cur.random)
        cur = cur.next
    return old_to_new[head]


if __name__ == "__main__":
    src = from_pairs([[7, None], [13, 0], [11, 4], [10, 2], [1, 0]])
    copied = copyRandomList(src)
    assert to_pairs(copied) == [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]
    assert copied is not src and copied.next is not src.next
    one = from_pairs([[1, 0]])
    assert to_pairs(copyRandomList(one)) == [[1, 0]]
    assert copyRandomList(None) is None
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先用本题的节点类型和辅助函数构造输入。比较节点值时转成列表或遍历序列；如果题目要求返回某个原节点或复制结构，还要用 `is` 检查对象身份。每个用例重新建节点，避免上一次调用改动了下一次的输入。

```python
src = from_pairs([[7, None], [13, 0], [11, 4], [10, 2], [1, 0]])
copied = copyRandomList(src)
assert to_pairs(copied) == [[7, None], [13, 0], [11, 4], [10, 2], [1, 0]]
assert copied is not src and copied.next is not src.next
one = from_pairs([[1, 0]])
assert to_pairs(copyRandomList(one)) == [[1, 0]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$。哈希写法额外空间 $O(n)$；交织复制额外空间 $O(1)$（不含新表）。

## Edge Cases

- 空表直接返回 `None`。
- 单节点的 `random` 指向自己时，哈希里能查到它自己的副本。
- 所有 `random` 都为空时，第二遍 `dict.get` 得到的都是 `None`。
- `random` 交叉或者指向前面的节点时，一定要先建完所有副本再接线。

## 追问

**能做到 $O(1)$ 额外空间吗？**
能，用三步交织，不建哈希。第一步在每个旧节点后面插入副本，变成 `A-A'-B-B'-C-C'`。第二步，如果 `cur.random` 非空，副本的 `random` 就是 `cur.random.next`，因为旧 random 的后继恰好是它的副本；`random` 为空时别解引用。第三步按奇偶拆链，旧表的 `next` 接回旧后继，新表的 `next` 接新后继。拆的时候要先保住 `copy.next` 再改 `cur.next`，不然旧表会断掉。时间还是 $O(n)$，额外空间 $O(1)$（不含新表）。白板上我会先画出这三步再写。

```python
def copyRandomListWeave(head):
    if head is None:
        return None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = Node(cur.val, nxt)
        cur = nxt
    cur = head
    while cur:
        if cur.random:
            cur.next.random = cur.random.next
        cur = cur.next.next
    dummy = Node(0)
    copy_tail, cur = dummy, head
    while cur:
        copy = cur.next
        cur.next = copy.next
        copy_tail.next = copy
        copy_tail = copy
        cur = cur.next
    return dummy.next
```

**克隆图（LC 133）怎么做？**
思路一样，先建副本再接线，只是邻居是一个列表，而且图里有环。哈希存 `旧节点 -> 新节点`，已经建过就直接返回，没建过就先 `Node(val)` 登记，再 DFS/BFS 去填 `neighbors`。一定要先放进哈希再走邻居，否则在环上会死循环。链表的 `random` 就相当于一条度为 $1$ 的额外边。独立卡见 `lc-133-clone-graph`。

```python
def cloneGraph(node):
    if node is None:
        return None
    mp = {}

    def dfs(cur):
        if cur in mp:
            return mp[cur]
        copy = Node(cur.val)
        mp[cur] = copy
        copy.neighbors = [dfs(nb) for nb in cur.neighbors]
        return copy

    return dfs(node)
```
