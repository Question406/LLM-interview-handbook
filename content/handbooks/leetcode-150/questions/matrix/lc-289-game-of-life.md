---
id: lc-289-game-of-life
section: matrix
order: 5
level: A
title: LC 289 · 生命游戏
quick: >-
  原地编码：活变死记 $-1$，死变活记 $2$。邻居用绝对值判「原来是否活」，最后解码回 $0/1$。时间
  $O(mn)$，额外空间 $O(1)$。
tags:
  - Matrix
  - Simulation
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 289. 生命游戏
    url: https://leetcode.cn/problems/game-of-life/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

细胞自动机：活细胞邻居为 $2$ 或 $3$ 则存活，否则死；死细胞恰好 $3$ 个活邻居则复活。按**同时**规则更新整盘，要求原地。

## 思路

直接改 $0/1$ 会污染还没算到的邻居。中间态：活$\to$死写成 $-1$，死$\to$活写成 $2$。统计邻居时看 `abs(board[ni][nj])==1`，读的是原始死活。最后正数变 $1$、其余变 $0$。

规则口诀：活的活在 $2$、$3$，死的只在 $3$ 复活。

## 参考代码

```python
from typing import List


def gameOfLife(board: List[List[int]]) -> None:
    m, n = len(board), len(board[0])
    dirs = (
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1), (0, 1),
        (1, -1), (1, 0), (1, 1),
    )
    for i in range(m):
        for j in range(n):
            live = 0
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and abs(board[ni][nj]) == 1:
                    live += 1
            if board[i][j] == 1 and (live < 2 or live > 3):
                board[i][j] = -1
            elif board[i][j] == 0 and live == 3:
                board[i][j] = 2
    for i in range(m):
        for j in range(n):
            board[i][j] = 1 if board[i][j] > 0 else 0


if __name__ == "__main__":
    a = [[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]]
    gameOfLife(a)
    assert a == [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]]
    b = [[1, 1], [1, 0]]
    gameOfLife(b)
    assert b == [[1, 1], [1, 1]]
    print("ok")
```

## 复杂度

时间 $O(mn)$，每格看至多 $8$ 个邻居。额外空间 $O(1)$。

## 边界

- $1\times 1$：邻居为 $0$，活细胞变死，死细胞保持死。
- 全死：下一状态仍全死。
- 全活：内部邻居 $8$ 个会过密变死，角落邻居 $3$ 个保持活。
- 边上细胞邻居不足 $8$ 个：越界不计入。

## 追问

- **无限棋盘或稀疏活细胞？** 不要存整盘。用集合记下当前活细胞坐标。每个活细胞给 $8$ 邻居 $+1$。下一轮：计数为 $3$ 的格子变活，计数为 $2$ 且当前是活的保持活。时间与活细胞数成正比。

```python
def gameOfLifeSparse(live):
    from collections import Counter
    cnt = Counter()
    for i, j in live:
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di or dj:
                    cnt[(i + di, j + dj)] += 1
    nxt = set()
    for p, c in cnt.items():
        if c == 3 or (c == 2 and p in live):
            nxt.add(p)
    return nxt
```

- **不能用负数？** 每个格子用 $2$ 比特打包：低位旧状态，高位新状态。统计邻居时只看 `board[ni][nj] & 1`。活且邻居为 $2$ 或 $3$、或死且邻居为 $3$，则 `|= 2`。最后统一 `>>= 1`。

```python
def gameOfLifeBits(board):
    m, n = len(board), len(board[0])
    dirs = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    for i in range(m):
        for j in range(n):
            live = 0
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n:
                    live += board[ni][nj] & 1
            if board[i][j] & 1:
                if live in (2, 3):
                    board[i][j] |= 2
            elif live == 3:
                board[i][j] |= 2
    for i in range(m):
        for j in range(n):
            board[i][j] >>= 1
```
