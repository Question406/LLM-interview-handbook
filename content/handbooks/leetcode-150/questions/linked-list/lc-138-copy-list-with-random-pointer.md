---
id: lc-138-copy-list-with-random-pointer
section: linked-list
order: 4
level: A
title: LC 138 · 随机链表的复制
quick: >-
  哈希旧节点映射到新节点：先扫一遍建副本，再扫一遍接 `next` / `random`。或三步交织复制省哈希。时间
  $O(n)$，哈希空间 $O(n)$。
tags:
  - Linked List
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 138. 随机链表的复制
    url: https://leetcode.cn/problems/copy-list-with-random-pointer/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

每个节点除 `next` 外还有 `random`，可指向表中任意节点或空。返回整表的深拷贝：新节点值相同，指针指向新表对应节点，不能复用旧节点。

## 思路

哈希表记「旧节点 $\to$ 新节点」。第一遍只按 `next` 建副本并入库；第二遍用哈希给每个新节点接上 `next` 和 `random`。`random` 为空时用 `dict.get` 得到 `None`。

空间优化：在每个旧节点后面插入副本，再按「旧.random 的后继」改副本的 `random`，最后拆成两条链。面试先写哈希，再提交织三步。

## 参考代码

```python
from typing import List, Optional


class Node:
    def __init__(self, x: int, next: Optional["Node"] = None, random: Optional["Node"] = None):
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
    return [[n.val, index[id(n.random)] if n.random is not None else None] for n in nodes]


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

## 复杂度

时间 $O(n)$。哈希写法额外空间 $O(n)$；交织复制额外空间 $O(1)$（不含新表）。

## 边界

- 空表：直接返回 `None`。
- 单节点 `random` 指向自己：哈希里能查到自己的副本。
- 所有 `random` 为空：第二遍 `dict.get` 得到 `None`。
- `random` 形成交叉、后向指针：必须先建完所有副本再接线。

## 追问

- **$O(1)$ 额外空间怎么拷？** 三步交织，不建哈希。第一步：在每个旧节点后面插入副本，变成 `A-A'-B-B'-C-C'`。第二步：若 `cur.random` 非空，则副本的 `random` 就是 `cur.random.next`（旧 random 的后继恰好是它的副本）。第三步：按奇偶拆链，把旧表 `next` 接回旧后继、新表 `next` 接新后继。拆时必须先保住 `copy.next`，再改 `cur.next`，否则旧表断掉。时间仍 $O(n)$，额外空间 $O(1)$（不含新表）。`random` 为空时不要解引用。面试先画三步再写。

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

- **图的克隆（LC 133）？** 同样「先建副本再接线」，但邻居是列表且图有环。哈希 `旧节点 -> 新节点`：若已建过直接返回，否则先 `Node(val)` 登记再 DFS/BFS 填 `neighbors`。必须先放入哈希再走邻居，否则环上死循环。链表的 `random` 就是度为 $1$ 的额外边。独立卡见 `lc-133-clone-graph`。

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
