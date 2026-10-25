---
id: ali-oa-match3
section: alibaba-oa
order: 21
level: A
title: 阿里 2022.03.14：消消乐大模拟的稳定写法？
quick: >-
  循环做「标记所有可消连通块 → 一次性清空 → 按列下落」，直到某一轮没有可消的块。同一轮先全部标记再删，边扫边改会漏消。
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

## 题目描述

给定带空位的彩色棋盘，反复消除达到大小阈值的同色连通块，再让每列中的剩余格子向下落，直到棋盘稳定。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `stabilize(board, k=3)`。board 是非空矩形整数列表，0 表示空位，正整数表示颜色；k 为正整数。相同颜色只通过上、下、左、右连接，对角线不连接。

### 输出与约束

每轮先找出全部大小至少为 k 的同色连通块，同时把这些位置变成 0；随后每列非零元素向下移动并保持列内相对顺序，上方补 0。原地修改 board 并返回稳定棋盘。不计算分数。列重力与默认 k=3 是手册重构约定。

### 示例

```text
board=[[1,1,1]], k=3 -> [[0,0,0]]
board=[[1,1]], k=3 -> [[1,1]]
单独对 [[1],[0],[2]] 应用 gravity 后 -> [[0],[1],[2]]
```

## 解题思路与参考答案

我会写成一个循环：每轮先把所有达标的同色连通块都找出来，统一清空，再让每列下落，直到某一轮没有新消除。关键在于同一轮里先标记、后删除，搜索途中不改棋盘。

## 真题记录

阿里 2022.03.14 研发压轴题的公开回忆：给定棋盘与消除规则（通常是同色连通块大小达到阈值），反复消除并下落，输出终局或得分。

## 题面

（公开回忆等价转述）给定 $n\times m$ 棋盘，格子是正整数颜色，空位记为 $0$。反复执行：

1. 找出所有四连通、颜色相同且大小 $\ge k$ 的连通块（公开回忆通常 $k=3$）
2. 这些格子同时消成空
3. 每列剩余格子向下坠落，上方补空

直到某一轮没有新消除，输出终局棋盘。

公开回忆没有完整数据范围，也没有统一规定「行重力还是列重力、是否计分」。下面按列向下坠落、$k=3$、只输出终局来写，不假装有官方计分公式。

输入假设第一行是 $n,m$，随后 $n$ 行、每行 $m$ 个整数；输出 $n$ 行终局。

## 思路

同一轮里可能有好几块同时达标，必须先全部标记，再统一清空。边搜边改的话，本该同时消掉的邻居会提前断开。

另一个要点是多轮。比如只有一列，从上到下是 `2 1 1 1 2 2`：第一轮消掉三个 `1`，下落后变成 `0 0 0 2 2 2`，第二轮三个 `2` 连上了，再消一次。所以外层要一直循环到没有新消除。

做法是外层 `while True`，每一轮用 `visited` 对非空格做 BFS/DFS 收集连通块，大小 $\ge 3$ 的加入删除集合；集合为空就结束。删除后对每一列从底往上压实非零，再把这一列写回。

这和三消「同一帧结算」一致：连通性按当前棋盘一次性判定。重力只改变空位，本轮不再结算新消除，新组合留给下一轮。输出时空位字符和行列方向要对上题面；如果题目是「行向左压实」，只改重力函数就行。

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

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

棋盘会原地修改，所以每条断言创建新棋盘。三块相连应消除，两块不够；单独测重力，确认非零元素向下落且顺序不变。

```python
assert stabilize([[1, 1, 1]]) == [[0, 0, 0]]
assert stabilize([[1, 1]]) == [[1, 1]]
board = [[1], [0], [2]]
gravity(board)
assert board == [[0], [1], [2]]
print("simple tests passed")
```

## 复杂度

每轮扫描 $O(nm)$，最坏每轮至少消 $k$ 个，轮数 $O(nm/k)$，总时间 $O(n^2 m^2/k)$。笔试网格通常不大。

## 边界

全空棋盘直接输出；整列同色 $\ge 3$ 一次消光；消完坠落后再构成新三连，必须多轮。$k=1$ 会清空所有非空格，公开规则不是这样。

## 追问

**搜到一块就立刻删，会怎样？**
相邻的同色块会被拆开，导致漏消。

**重力方向写错会怎样？**
向上落或者按行压缩，终局和样例对不上。

**四连通还是八连通？**
四连通，只算横竖、不算斜。写成八连通就和公开回忆对不上了。

**要计分怎么办？**
常见是按块大小给分，或者连消加成。公式没公开就别编，先问清楚，再改 `mark_and_clear` 的返回值。
