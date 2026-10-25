---
id: lc-841-keys-and-rooms
section: graph-dfs
order: 1
level: S
title: LC 841 · 钥匙和房间
quick: "房间是点，钥匙是有向边。从 $0$ 号房 DFS，能到的都标记，最后看是否全部访问过。时间 $O(n+k)$（$k$ 是钥匙总数），额外空间 $O(n)$。"
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

## 题目描述

有 n 个房间，编号为 0 到 n-1，开始时只有 0 号房未锁。进入房间 i 后，可以拿到 rooms[i] 中列出的所有钥匙；钥匙值 j 代表它能打开 j 号房。判断能否从 0 号房出发，最终进入所有房间。

### 输入与输出

实现 `canVisitAllRooms(rooms: List[List[int]]) -> bool`。拿到的钥匙可以一直使用；可以自由返回已经打开的房间，没有必要按房号顺序访问。

### 约束

- `2 <= n <= 1000`。
- 每个钥匙值在 0 到 n-1；同一个房间中的钥匙值互不相同，不同房间可以提供相同钥匙。
- 每间房最多有 1000 把钥匙，总钥匙数在 1 到 3000。

### 示例

```text
输入：rooms = [[1],[2],[3],[]]
输出：true
```

示例中可以依次进入 0、1、2、3 号房，因而返回 True。

## 解题思路与参考答案

## 题意

有 $n$ 个房间，编号 $0$ 到 $n-1$，只有 $0$ 号房一开始没锁。`rooms[i]` 是进入房间 $i$ 后能拿到的钥匙列表，钥匙 $x$ 能开房间 $x$。钥匙可以重复。问能否进入所有房间。

## 思路

这就是一次有向图的可达性遍历，我从 $0$ 号房 DFS。房间 $i$ 里有钥匙 $x$，就连一条有向边 $i\to x$，问题变成从 $0$ 出发能不能到达所有点。钥匙拿到后随时可以回去开门，顺序不影响能到哪儿，所以遍历一遍就够。

拿 `[[1],[2],[3],[]]` 走一遍：$0$ 号房拿到 $1$ 的钥匙，$1$ 号房拿到 $2$ 的，$2$ 号房拿到 $3$ 的，四间都进去了，返回真。

我用显式栈做 DFS，入栈时就标 `seen`，同一个房间不会被压两次，最后看 `all(seen)`。换成队列做 BFS 也一样。

边是有向的：$a$ 里有 $b$ 的钥匙，不代表 $b$ 里有 $a$ 的钥匙，所以用无向的并查集判连通会出错。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert canVisitAllRooms([[1], [2], [3], []]) is True
assert canVisitAllRooms([[1, 3], [3, 0, 1], [2], [0]]) is False
assert canVisitAllRooms([[]]) is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n+k)$，$k$ 是所有钥匙的总数，每个房间出栈一次、每把钥匙看一次。额外空间 $O(n)$。

## 边界

只有一个房间，`[[]]`，直接为真。

$0$ 号房没有钥匙而 $n\gt 1$ 时，除了自己都进不去，返回假。

重复钥匙、指向自己或已开房间的钥匙，都被 `seen` 挡掉，不会重复入栈。

## 追问

**递归 DFS 可以吗？**
可以，但 $n$ 最多 $1000$，一条很长的访问路径会接近 Python 默认的递归上限 $1000$，得调 `sys.setrecursionlimit`。面试里我直接写显式栈，省掉这个坑。

**要返回进不去的房间呢？**
遍历完把 `seen` 为假的下标收集起来就行，复杂度不变。

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

**和省份数量那题有什么区别？**
`lc-547-number-of-provinces` 是无向图数连通块，这题是有向图单源可达。
