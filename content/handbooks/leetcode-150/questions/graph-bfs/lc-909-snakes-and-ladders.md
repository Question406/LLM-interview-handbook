---
id: lc-909-snakes-and-ladders
section: graph-bfs
order: 1
level: A
title: LC 909 · 蛇梯棋
quick: >-
  把格子按蛇形编号 $1..n^2$ 当成一维的点做 BFS，每步枚举掷出 $1..6$，落到蛇或梯子就强制传送。先写对「编号
  $\leftrightarrow$ 行列」的映射，BFS 第一次到达 $n^2$ 的步数就是答案，到不了返回 $-1$。
tags:
  - BFS
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 909. 蛇梯棋
    url: 'https://leetcode.cn/problems/snakes-and-ladders/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定 n×n 的蛇梯棋棋盘，格子从左下角的 1 开始按行蛇形编号：最底行从左向右，上一行从右向左，之后交替，直到 n²。你从格子 1 出发，每次掷骰可选择前进 1 到 6 格，不能越过终点；若落点写着非 -1 的值，必须立即传送到该编号。一次掷骰最多执行一次传送，即使传送终点还有蛇或梯子也不继续连跳。求到达格子 n² 的最少掷骰次数。

### 输入与输出

实现 `snakesAndLadders(board) -> int`。`board[r][c] == -1` 表示普通格，否则为传送目标编号；若无法到达终点，返回 -1。

### 约束与约定

- `2 <= n <= 20`，board 是正方形。
- 格子值为 -1 或 `[1,n*n]` 中的编号。
- 起点 1 与终点 n² 都不是蛇或梯子的起始格。

### 示例

```text
输入：board = [[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1],[-1,35,-1,-1,13,-1],[-1,-1,-1,-1,-1,-1],[-1,15,-1,-1,-1,-1]]
输出：4
```

示例返回 4，表示存在四次掷骰到达终点的路线，且不存在更少掷骰的路线。

[官方原题与完整题面](https://leetcode.com/problems/snakes-and-ladders/description/)。

## 解题思路与参考答案

## 题意

$n\times n$ 棋盘，格子从左下角起按行蛇形编号 $1..n^2$（偶数行从下往上数时从左到右，奇数行从右到左）。从 $1$ 出发，每步掷骰 $1..6$；落点的 `board` 值不是 $-1$ 时，必须传送到该值。求到达 $n^2$ 的最少掷次，到不了返回 $-1$。

## 思路

我会把棋盘压成一维再做 BFS。每掷一次骰子代价都是 $1$，求最少掷次就是无权图的最短路。

先处理编号到坐标的映射。编号 $s$ 在从底数起的第 `r=(s-1)//n` 行、第 `c=(s-1)%n` 列，奇数行要把 `c` 镜像，最后映射到矩阵的第 `n-1-r` 行。比如 $n=6$ 时，编号 $7$ 在从底数的第 $1$ 行，这一行从右往左走，所以它在矩阵的第 $4$ 行、最右一列。

然后做 BFS：从当前格枚举 $s+1..s+6$（不超过终点），落到蛇或梯子就改成传送目标，每个落点只入队一次。传送不会链式发生，题目保证目的地不再是蛇或梯子。白板上我先写清「编号 $\leftrightarrow$ 行列」，再写 BFS，别在二维格子上硬走。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
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
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n^2)$，空间 $O(n^2)$。每个格子至多入队一次，出队后只枚举常数个骰点。

## Edge Cases

$n=1$ 时已经在终点，掷 $0$ 次；实现上起点以 `steps=0` 入队，出队就立刻返回。蛇或梯子可以指向更前或更后，传送后编号变大是梯子、变小是蛇，BFS 照样走，访问集合（vis）防止死循环。没有蛇梯时每步最多 $+6$，答案是 $\lceil (n^2-1)/6\rceil$；编号和行列的映射仍要写对，蛇形行不能走错。

## 追问

**可以选择不传送吗？**
原题是强制传送：落到非 $-1$ 的格子必须走蛇或梯子，目的地不再是蛇梯，不会链式跳。改成可选就是另一道题了：状态仍是格子，从 $s$ 掷到 $t$ 后，若 `board[t]!=-1`，可以停在 $t$，也可以去传送点，边数都算 $1$。vis 要按最终停下的格子标记，否则强制和可选会把最短路剪错。

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

**为什么不用 Dijkstra？**
每次掷骰代价都是 $1$，无权最短路用 BFS 就是最优的，堆优化没有收益。如果「掷 $k$ 点代价为 $k$」，或者格子有不同的过路费，边权不再恒为 $1$，才换成 Dijkstra 或 0-1 BFS。
