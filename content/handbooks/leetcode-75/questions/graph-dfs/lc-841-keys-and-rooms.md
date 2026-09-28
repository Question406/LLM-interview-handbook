---
id: lc-841-keys-and-rooms
section: graph-dfs
order: 1
level: S
title: LC 841 · 钥匙和房间
quick: >-
  房间是点，钥匙是有向边。从 $0$ 号房 DFS，能到的都标记，最后看是否全部访问过。时间
  $O(n+k)$，$k$ 是钥匙总数，额外空间 $O(n)$。
tags:
  - Graph
  - DFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 841. Keys and Rooms
    url: https://leetcode.com/problems/keys-and-rooms/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

有 $n$ 个房间，编号 $0$ 到 $n-1$，只有 $0$ 号房一开始没锁。`rooms[i]` 是进入房间 $i$ 后能拿到的钥匙列表，钥匙 $x$ 能开房间 $x$。钥匙可以重复。问能否进入所有房间。

## 思路

把房间 $i$ 到它钥匙里每个房间 $x$ 连一条有向边 $i\to x$，问题变成：从 $0$ 出发，能否到达所有点。拿到钥匙后随时可以回去开门，顺序不影响可达性，所以就是一次图遍历。

我用显式栈做 DFS：入栈时就标 `seen`，同一个房间不会被压两次。最后 `all(seen)`。BFS 换成队列也一样。

注意边是有向的：$a$ 里有 $b$ 的钥匙不代表 $b$ 里有 $a$ 的钥匙，所以不能用无向的并查集来判连通。

## 参考代码

```python
from typing import List


def canVisitAllRooms(rooms: List[List[int]]) -> bool:
    seen = [False] * len(rooms)
    seen[0] = True
    stack = [0]
    while stack:
        room = stack.pop()
        for key in rooms[room]:
            if not seen[key]:
                seen[key] = True
                stack.append(key)
    return all(seen)


if __name__ == "__main__":
    assert canVisitAllRooms([[1], [2], [3], []]) is True
    assert canVisitAllRooms([[1, 3], [3, 0, 1], [2], [0]]) is False
    assert canVisitAllRooms([[]]) is True
    assert canVisitAllRooms([[1], []]) is True
    assert canVisitAllRooms([[], [0]]) is False
    assert canVisitAllRooms([[1, 1, 1], [2, 0], []]) is True
    print("ok")
```

## 复杂度

时间 $O(n+k)$，$k$ 是所有钥匙的总数，每个房间出栈一次、每把钥匙看一次。额外空间 $O(n)$。

## 边界

- 只有一个房间：`[[]]` 直接为真。
- $0$ 号房没有钥匙而 $n\gt 1$：除自己外都进不去，返回假。
- 重复钥匙、指向自己或已开房间的钥匙：`seen` 挡掉，不会重复入栈。

## 追问

- **递归 DFS 可以吗？** 可以，但 $n$ 最多 $1000$ 时一条长链会接近 Python 默认递归上限 $1000$，需要 `sys.setrecursionlimit`。面试里我直接写显式栈，省掉这个坑。
- **要返回进不去的房间？** 遍历完把 `seen` 为假的下标收集起来即可，复杂度不变。和 `lc-547-number-of-provinces` 对比：那题是无向图数连通块，这题是有向图单源可达。

```python
def lockedRooms(rooms):
    seen = [False] * len(rooms)
    seen[0] = True
    stack = [0]
    while stack:
        for key in rooms[stack.pop()]:
            if not seen[key]:
                seen[key] = True
                stack.append(key)
    return [i for i, ok in enumerate(seen) if not ok]
```
