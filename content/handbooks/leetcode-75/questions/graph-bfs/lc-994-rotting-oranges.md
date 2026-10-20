---
id: lc-994-rotting-oranges
section: graph-bfs
order: 2
level: S
title: LC 994 · 腐烂的橘子
quick: >-
  多源 BFS：所有烂橘子一起作为第 $0$ 层入队，一层就是一分钟，同时数新鲜橘子。BFS 结束后还有新鲜的返回
  $-1$，否则返回层数。时间 $O(mn)$，额外空间 $O(mn)$。
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
  - title: 994. Rotting Oranges
    url: https://leetcode.com/problems/rotting-oranges/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

$m\times n$ 网格，$0$ 空、$1$ 新鲜橘子、$2$ 烂橘子。每过一分钟，烂橘子上下左右相邻的新鲜橘子都会变烂。返回所有橘子都烂掉所需的最少分钟数；不可能则返回 $-1$。

## 思路

每个新鲜橘子变烂的时间，等于它到最近烂橘子的网格距离。把所有初始烂橘子一起放进队列当第 $0$ 层，BFS 每扩一层就是一分钟，这样每个格子第一次被访问时的层数就是它到最近源的距离。

开始时数一下新鲜橘子 `fresh`，每烂一个减一。BFS 结束后 `fresh` 还大于 $0$ 说明有橘子被隔开，返回 $-1$。分钟数只在「这一层确实烂了新橘子」时才加，避免最后一层空扩多算一分钟。

常见误区是：对每个烂橘子单独跑 BFS 再取最小值，烂橘子多时是 $O(k\cdot mn)$。多源一起入队只需一次。

## 参考代码

```python
from collections import deque
from typing import List


def orangesRotting(grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 2:
                q.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while q and fresh:
        for _ in range(len(q)):
            r, c = q.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))
        minutes += 1
    return -1 if fresh else minutes


if __name__ == "__main__":
    assert orangesRotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
    assert orangesRotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
    assert orangesRotting([[0, 2]]) == 0
    assert orangesRotting([[0]]) == 0
    assert orangesRotting([[1]]) == -1
    assert orangesRotting([[2, 1, 1, 1, 2]]) == 2
    print("ok")
```

## 复杂度

时间 $O(mn)$，每个格子最多入队一次。额外空间 $O(mn)$，最坏整张网格都在队列里。

## 边界

- 一开始没有新鲜橘子：返回 $0$，即使也没有烂橘子。
- 有新鲜橘子但没有烂橘子：循环不进，`fresh` 大于 $0$，返回 $-1$。
- 两端各有一个烂橘子向中间扩：多源同时推进，时间是到最近源的距离，不是到某个固定源的距离。

## 追问

- **不能改输入怎么办？** 另开 `dist` 矩阵或 `seen` 集合记录已烂的格子，逻辑相同，空间仍是 $O(mn)$。
- **要每个橘子变烂的具体时间？** 用 `dist[r][c]` 记录入队时的层数，就是多源最短距离。和 `lc-1926-nearest-exit-from-entrance-in-maze` 一样，都是网格上的无权最短路，只是这题的源有多个。

```python
from collections import deque

def rotTimes(grid):
    m, n = len(grid), len(grid[0])
    dist = [[-1] * n for _ in range(m)]
    q = deque()
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 2:
                dist[r][c] = 0
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1 and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist
```
