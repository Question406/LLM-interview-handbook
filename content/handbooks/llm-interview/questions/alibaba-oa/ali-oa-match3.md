---
id: ali-oa-match3
section: alibaba-oa
order: 21
level: A
title: 阿里 2022.03.14：消消乐大模拟的稳定写法？
quick: >-
  循环「标记可消连通块 → 一次性消去 → 重力下落」直到稳定。我会先标记再删，避免边扫边改漏消。
tags:
  - Alibaba
  - OA
  - 模拟
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题记录

- 公司 / 场次：阿里 2022.03.14 研发压轴（公开回忆）
- 题意：给定棋盘与消除规则（通常是同色连通块长度达到阈值），反复消除并下落，输出终局或得分。

## 题面

（公开回忆等价转述）给定 $n\times m$ 棋盘，格子是正整数颜色，空位记为 $0$。反复执行：

1. 找出所有四连通、颜色相同且大小 $\ge k$ 的连通块（公开回忆通常 $k=3$）
2. 这些格子同时消成空
3. 每列剩余格子向下坠落，上方补空

直到某一轮没有新消除。输出终局棋盘。

公开回忆没有完整数据范围，也没有统一规定「行重力还是列重力、是否计分」。下面按**列向下坠落**、$k=3$、只输出终局，不假装有官方计分公式。

输入假设：第一行 $n,m$，随后 $n$ 行每行 $m$ 个整数。输出 $n$ 行终局。

## 思路

同一轮里多块可能同时达标，必须先全部标记再统一清空。边搜边改会让本该同时消掉的邻居提前断开。

算法：外层 `while True`。每一轮用 `visited` 对非空格做 BFS/DFS，收集连通块；大小 $\ge 3$ 的加入删除集合。若集合空则结束。删除后对每一列从底向上压实非零，再把该列写回。

这样写是对的：连通性按当前棋盘一次性判定，与「三消游戏同一帧结算」一致。重力只改变空位，不会在本轮制造新的「未结算消除」。新组合留给下一轮。

不要在搜索中途改棋盘。输出时注意空位字符与行列方向：若题面是「行向左压实」，只改重力函数。

## 参考代码

```python
import sys
from collections import deque

DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def collect_block(board, sx, sy, vis):
    n, m = len(board), len(board[0])
    color = board[sx][sy]
    q = deque([(sx, sy)])
    vis[sx][sy] = True
    cells = [(sx, sy)]
    while q:
        x, y = q.popleft()
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < m and not vis[nx][ny]:
                if board[nx][ny] == color:
                    vis[nx][ny] = True
                    q.append((nx, ny))
                    cells.append((nx, ny))
    return cells


def mark_and_clear(board, k=3):
    n, m = len(board), len(board[0])
    vis = [[False] * m for _ in range(n)]
    erase = []
    for i in range(n):
        for j in range(m):
            if board[i][j] == 0 or vis[i][j]:
                continue
            cells = collect_block(board, i, j, vis)
            if len(cells) >= k:
                erase.extend(cells)
    for x, y in erase:
        board[x][y] = 0
    return bool(erase)


def gravity(board):
    n, m = len(board), len(board[0])
    for j in range(m):
        stack = []
        for i in range(n - 1, -1, -1):
            if board[i][j] != 0:
                stack.append(board[i][j])
        for i in range(n - 1, -1, -1):
            board[i][j] = stack.pop(0) if stack else 0


def stabilize(board, k=3):
    while mark_and_clear(board, k):
        gravity(board)
    return board


def main():
    data = list(map(int, sys.stdin.read().split()))
    n, m = data[0], data[1]
    board = []
    t = 2
    for _ in range(n):
        board.append(data[t : t + m])
        t += m
    stabilize(board)
    for row in board:
        print(*row)


if __name__ == "__main__":
    main()
```

边界：全空棋盘直接输出；整列同色 $\ge 3$ 一次消光；消完坠落后再构成新三连，必须多轮。$k=1$ 会清空所有非空格，公开规则不是这样。

## 复杂度

每轮扫描 $O(nm)$，最坏每轮至少消 $k$ 个，轮数 $O(nm/k)$，总时间 $O(n^2 m^2/k)$。笔试网格通常不大。

## 易错 / 面试追问

- 搜索到一块立刻删除，导致相邻同色块被拆开、漏消。
- 重力方向写反（向上或按行压缩），终局和样例对不上。
- 只用横竖三连、不用斜，却写成八连通；公开回忆是四连通。
- 追问计分：常见是按块大小给分或连消加成。公式未公开就不要编，先问清再改 `mark_and_clear` 的返回值。
