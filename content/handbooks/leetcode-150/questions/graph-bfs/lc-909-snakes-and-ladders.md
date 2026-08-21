---
id: lc-909-snakes-and-ladders
section: graph-bfs
order: 1
level: A
title: LC 909 · 蛇梯棋
quick: >-
  棋盘蛇形编号 $1..n^2$。一维 BFS，每次掷 $1..6$；落到蛇/梯必须传送。求到达终点的最少步，到不了返回
  $-1$。
tags:
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 909. 蛇梯棋
    url: https://leetcode.cn/problems/snakes-and-ladders/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$n\times n$ 棋盘，格子从左下角起按行蛇形编号 $1..n^2$（偶数行从下往上从左到右，奇数行从右到左）。从 $1$ 出发，每步掷骰 $1..6$。若落点 `board` 不是 $-1$，必须传送到该值。求到 $n^2$ 的最少掷次；到不了返回 $-1$。

## 思路

把格子当成一维点。编号 $s$ 转坐标：从底数第 `r=(s-1)//n` 行，列 `c=(s-1)%n`，奇数行把 `c` 镜像，再映射到矩阵行 `n-1-r`。

BFS 求最短路：当前格出发枚举 $s+1..s+6$（不超过终点），落到蛇/梯就改成传送目标。每个落点只入队一次。传送不链式，题目保证目的地不再是蛇/梯。

面试先写清「编号 $\leftrightarrow$ 行列」，再写 BFS，别在二维上硬走。

## 参考代码

```python
from collections import deque
from typing import List, Tuple


def snakesAndLadders(board: List[List[int]]) -> int:
    n = len(board)
    dest = n * n

    def square_to_rc(s: int) -> Tuple[int, int]:
        r, c = divmod(s - 1, n)
        if r % 2 == 1:
            c = n - 1 - c
        return n - 1 - r, c

    q = deque([(1, 0)])
    seen = {1}
    while q:
        curr, steps = q.popleft()
        if curr == dest:
            return steps
        for nxt in range(curr + 1, min(curr + 6, dest) + 1):
            r, c = square_to_rc(nxt)
            land = board[r][c] if board[r][c] != -1 else nxt
            if land not in seen:
                seen.add(land)
                q.append((land, steps + 1))
    return -1


if __name__ == "__main__":
    board = [
        [-1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1],
        [-1, 35, -1, -1, 13, -1],
        [-1, -1, -1, -1, -1, -1],
        [-1, 15, -1, -1, -1, -1],
    ]
    assert snakesAndLadders(board) == 4
    assert snakesAndLadders([[-1, -1], [-1, 3]]) == 1
    print("ok")
```

## 复杂度

时间 $O(n^2)$，空间 $O(n^2)$。每个格子入队至多一次，出队后枚举常数个骰点。

## 边界

- $n=1$：已在终点，掷 $0$ 次。实现上起点入队 `steps=0`，出队立刻返回。
- 蛇/梯可指向更前或更后：传送后编号变大是梯子、变小是蛇；BFS 照样走，vis 防死循环。
- 无蛇梯：每步最多 $+6$，答案是 $\lceil (n^2-1)/6\rceil$。编号 $\leftrightarrow$ 行列映射仍要写对，蛇形行不能走错。

## 追问

- **可以不传送？** 题目是强制传送：落到非 $-1$ 必须走蛇/梯，目的地不再是蛇/梯，不会链式跳。做成「可选」就变成另一题：状态仍是格子，从编号 $s$ 掷到 $t$ 后，若 `board[t]!=-1`，可以停在 $t$ 也可以去传送点，边数仍为 $1$。vis 要按**最终停下的格子**标记，否则强制/可选会把最短路剪错。

```python
from collections import deque

def snakesOptionalTeleport(board):
    n = len(board)
    dest = n * n

    def square_to_rc(s):
        r, c = divmod(s - 1, n)
        if r % 2 == 1:
            c = n - 1 - c
        return n - 1 - r, c

    q = deque([(1, 0)])
    seen = {1}
    while q:
        curr, steps = q.popleft()
        if curr == dest:
            return steps
        for nxt in range(curr + 1, min(curr + 6, dest) + 1):
            r, c = square_to_rc(nxt)
            options = [nxt]
            if board[r][c] != -1:
                options.append(board[r][c])
            for land in options:
                if land not in seen:
                    seen.add(land)
                    q.append((land, steps + 1))
    return -1
```

- **为何不用 Dijkstra？** 每次掷骰代价都是 $1$，无权最短路 BFS 即为最优，堆优化没有收益。若「掷 $k$ 点代价为 $k$」或格子有不同过路费，边权不再恒 $1$，才改 Dijkstra / 0-1 BFS。
