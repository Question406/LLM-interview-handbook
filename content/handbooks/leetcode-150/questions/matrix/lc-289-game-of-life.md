---
id: lc-289-game-of-life
section: matrix
order: 5
level: A
title: LC 289 · 生命游戏
quick: >-
  原地用中间编码同时存新旧状态，活变死记 $-1$，死变活记 $2$。数邻居时用绝对值判断「原来是不是活的」，最后统一 decoding 回 $0/1$。时间
  $O(mn)$，额外空间 $O(1)$。
tags:
  - Matrix
  - Simulation
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 289. 生命游戏
    url: 'https://leetcode.cn/problems/game-of-life/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定由 0/1 构成的细胞网格 board，1 表示活细胞，0 表示死细胞。一个格子的邻居是周围最多八个格子，不包括自己：活细胞恰有 2 或 3 个活邻居时继续存活，否则死亡；死细胞恰有 3 个活邻居时复活。把整个网格推进一代。

### 接口与输出

实现 `gameOfLife(board: List[List[int]]) -> None`，原地修改 board。所有新状态必须根据同一份更新前状态决定，不能让本代已修改的格子影响其他格子的判定。

### 合法输入与约束

行数和列数均为 1 到 25，所有格子为整数 0 或 1。网格不会环绕，grid 外的 cells 不计入 live neighbours；示例输出展示调用后的 board，不是函数返回值。

### 示例

```text
输入：board = [[0,1,0],[0,0,1],[1,1,1],[0,0,0]]
输出：[[0,0,0],[1,0,1],[0,1,1],[0,1,0]]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/game-of-life/description/)。

## 解题思路与参考答案

## 题意

细胞自动机。活细胞的活邻居为 $2$ 或 $3$ 个就存活，否则死去；死细胞恰好有 $3$ 个活邻居就复活。整盘按同一时刻的规则更新，要求原地完成。

## 思路

我用中间编码在原地更新，因为所有格子都要根据同一轮的旧状态来算，直接覆盖成 $0/1$，后面的格子就会读到新状态。活变死写成 $-1$，死变活写成 $2$，这样旧状态和新状态都留在格子里。数邻居时看 `abs(board[ni][nj])==1`，读到的是原来的死活。全部算完后，正数变 $1$，其余变 $0$。

比如某个活细胞已经被标成 $-1$，它右边的格子数邻居时看到 `abs(-1)==1`，照样把它当活的算；一个刚被标成 $2$ 的格子，绝对值是 $2$，也还是按原来的死细胞算。

规则可以记成一句话，活的在邻居为 $2$、$3$ 时活下来，死的只在恰好 $3$ 个时复活。

## 参考代码

```python
from typing import List


def gameOfLife(board: List[List[int]]) -> None:
    m, n = len(board), len(board[0])
    dirs = (
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
a = [[0, 1, 0], [0, 0, 1], [1, 1, 1], [0, 0, 0]]
gameOfLife(a)
assert a == [[0, 0, 0], [1, 0, 1], [0, 1, 1], [0, 1, 0]]
b = [[1, 1], [1, 0]]
gameOfLife(b)
assert b == [[1, 1], [1, 1]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，每格最多看 $8$ 个邻居。额外空间 $O(1)$。

## Edge Cases

- $1\times 1$ 时没有邻居，活细胞变死，死细胞还是死。
- 全死时下一轮仍然全死。
- 全活时内部格子有 $8$ 个邻居，过密变死；角落只有 $3$ 个邻居，保持活。
- 边上的细胞邻居不足 $8$ 个，越界的不计入。

## 追问

**棋盘无限大，或者活细胞很稀疏呢？**
别存整盘，用集合记下当前活细胞的坐标。每个活细胞给自己的 $8$ 个邻居计数加一，下一轮计数为 $3$ 的格子变活，计数为 $2$ 且当前是活的保持活。时间和活细胞数成正比。

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

**不让用负数怎么办？**
每个格子用 $2$ 个比特打包，低位存旧状态，高位存新状态。数邻居时只看 `board[ni][nj] & 1`；活且邻居为 $2$ 或 $3$，或者死且邻居为 $3$，就 `|= 2`。最后统一 `>>= 1`。

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
