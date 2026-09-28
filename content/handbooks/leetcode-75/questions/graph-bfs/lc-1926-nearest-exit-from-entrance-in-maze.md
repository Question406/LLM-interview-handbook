---
id: lc-1926-nearest-exit-from-entrance-in-maze
section: graph-bfs
order: 1
level: A
title: LC 1926 · 迷宫中离入口最近的出口
quick: >-
  网格无权最短路，从入口 BFS，第一次扩展到的边界空格就是最近出口，入口本身不算。时间 $O(mn)$，额外空间
  $O(mn)$。
tags:
  - Graph
  - BFS
  - Matrix
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1926. Nearest Exit from Entrance in Maze
    url: https://leetcode.com/problems/nearest-exit-from-entrance-in-maze/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

$m\times n$ 迷宫，`'.'` 是空格，`'+'` 是墙。从 `entrance = [r, c]`（保证是空格）出发，每步上下左右走一格，不能穿墙、不能出界。出口是位于边界上的空格，但入口自己不算出口。返回到最近出口的步数，没有则返回 $-1$。

## 思路

每步代价都是 $1$，最短步数就是 BFS 层数。从入口入队，按层往外扩，第一次扩展到的边界空格一定最近，直接返回。

入队时就标记已访问，而不是出队时标，否则同一格会被多个邻居重复入队。判断出口放在「扩展邻居」这一步做：入口在边界上也不会被误判，因为入口是起点，从未作为邻居被检查过。

DFS 能找到某个出口，但找不到最短的那个，要枚举所有路径，指数级。

## 参考代码

```python
from collections import deque
from typing import List


def nearestExit(maze: List[List[str]], entrance: List[int]) -> int:
    m, n = len(maze), len(maze[0])
    r0, c0 = entrance
    seen = [[False] * n for _ in range(m)]
    seen[r0][c0] = True
    q = deque([(r0, c0, 0)])
    while q:
        r, c, d = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < m and 0 <= nc < n):
                continue
            if maze[nr][nc] != "." or seen[nr][nc]:
                continue
            if nr in (0, m - 1) or nc in (0, n - 1):
                return d + 1
            seen[nr][nc] = True
            q.append((nr, nc, d + 1))
    return -1


if __name__ == "__main__":
    maze = [["+", "+", ".", "+"], [".", ".", ".", "+"], ["+", "+", "+", "."]]
    assert nearestExit(maze, [1, 2]) == 1
    maze = [["+", "+", "+"], [".", ".", "."], ["+", "+", "+"]]
    assert nearestExit(maze, [1, 0]) == 2
    assert nearestExit([[".", "+"]], [0, 0]) == -1
    assert nearestExit([["."]], [0, 0]) == -1
    maze = [["+", ".", "+"], ["+", ".", "+"], ["+", "+", "+"]]
    assert nearestExit(maze, [1, 1]) == 1
    maze = [["+", "+", "+"], ["+", ".", "+"], ["+", "+", "+"]]
    assert nearestExit(maze, [1, 1]) == -1
    print("ok")
```

## 复杂度

时间 $O(mn)$，每个格子最多入队一次。额外空间 $O(mn)$，`seen` 与队列。

## 边界

- 入口在边界上：它不算出口，要找别的边界空格；代码只在邻居上判出口，天然满足。
- 只有入口一个空格（如 `[["."]]`）：无出口，返回 $-1$。
- 被墙围死：队列耗尽返回 $-1$。

## 追问

- **要输出最短路径本身？** BFS 时记每个格子的前驱 `parent[(nr, nc)] = (r, c)`，找到出口后沿前驱回溯到入口再反转。复杂度不变。
- **多个入口，问任一入口到任一出口的最短距离？** 多源 BFS：所有入口一起作为第 $0$ 层入队，其余不变。`lc-994-rotting-oranges` 是同一个多源写法。

```python
from collections import deque

def nearestExitMulti(maze, entrances):
    m, n = len(maze), len(maze[0])
    starts = {tuple(e) for e in entrances}
    seen = set(starts)
    q = deque((r, c, 0) for r, c in starts)
    while q:
        r, c, d = q.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < m and 0 <= nc < n and maze[nr][nc] == "." and (nr, nc) not in seen:
                if (nr in (0, m - 1) or nc in (0, n - 1)) and (nr, nc) not in starts:
                    return d + 1
                seen.add((nr, nc))
                q.append((nr, nc, d + 1))
    return -1
```
