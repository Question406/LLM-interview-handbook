---
id: lc-130-surrounded-regions
section: graph
order: 2
level: A
title: LC 130 · 被围绕的区域
quick: >-
  被围住的 `'O'` 才改 `'X'`。先从边界 `'O'` DFS 标记「能通到边界」，再把未标记的 `'O'` 改
  `'X'`。时间 $O(mn)$。
tags:
  - DFS
  - Grid
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 130. 被围绕的区域
    url: https://leetcode.cn/problems/surrounded-regions/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$m\times n$ 棋盘，`'X'` 与 `'O'`。把所有被 `'X'` 四连通围住的 `'O'` 改成 `'X'`。能通到边界的 `'O'` 不算被围，保持原样。原地修改。

## 思路

被围 = 不能走到边界。反过来做：从四条边上的 `'O'` 出发 DFS/BFS，把连通到边界的整片标成临时符（如 `'#'`）。然后扫全盘：剩下的 `'O'` 必被围，改 `'X'`；`'#'` 改回 `'O'`。

不要从内部 `'O'` 出发再判断是否碰边，容易漏连通、也更慢。面试一句：「先保边界，再翻内部」。

## 参考代码

```python
from typing import List


def solve(board: List[List[str]]) -> None:
    if not board:
        return
    m, n = len(board), len(board[0])

    def dfs(r: int, c: int) -> None:
        if r < 0 or r >= m or c < 0 or c >= n or board[r][c] != "O":
            return
        board[r][c] = "#"
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for i in range(m):
        dfs(i, 0)
        dfs(i, n - 1)
    for j in range(n):
        dfs(0, j)
        dfs(m - 1, j)

    for i in range(m):
        for j in range(n):
            if board[i][j] == "O":
                board[i][j] = "X"
            elif board[i][j] == "#":
                board[i][j] = "O"


if __name__ == "__main__":
    a = [
        ["X", "X", "X", "X"],
        ["X", "O", "O", "X"],
        ["X", "X", "O", "X"],
        ["X", "O", "X", "X"],
    ]
    solve(a)
    assert a == [
        ["X", "X", "X", "X"],
        ["X", "X", "X", "X"],
        ["X", "X", "X", "X"],
        ["X", "O", "X", "X"],
    ]
    b = [["X"]]
    solve(b)
    assert b == [["X"]]
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$（递归栈）。每个格子被标记常数次。

## 边界

- $1\times n$ / $m\times 1$：每个格子都在边界，`'O'` 全部保留，一次都不翻。
- 整盘 `'O'`：四边出发会把整盘标成 `'#'`，最后全改回 `'O'`。
- 内部封闭一块：边界 DFS 碰不到，第二遍扫盘时改成 `'X'`。
- 与「沉岛计数」对偶：本题保边界、翻内部；岛屿数量是淹所有陆地。见 LC 200，独立卡 `lc-200-number-of-islands`。

## 追问

- **「被围」改成八连通？** 标记边界连通块时八个方向都走（含对角线）。内部翻盘仍只处理没被标记的 `'O'`。注意：八连通「围住」更难发生——对角也能漏出去，被围区域会变少。

```python
DIRS8 = (
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
)

def markBorder8(board, r, c):
    m, n = len(board), len(board[0])
    if r < 0 or r >= m or c < 0 or c >= n or board[r][c] != "O":
        return
    board[r][c] = "#"
    for dr, dc in DIRS8:
        markBorder8(board, r + dr, c + dc)
```

- **统计被围区域块数（不是改盘）？** 仍先从边界 `'O'` 出发，把能逃出去的整片标掉。然后对剩下的 `'O'` 再跑一遍「沉岛」：每发现一块计数加一并淹掉。算法就是 LC 200 套在「去掉边界连通之后的盘」上。

```python
def countSurrounded(board):
    m, n = len(board), len(board[0])

    def dfs(r, c, src, dst):
        if r < 0 or r >= m or c < 0 or c >= n or board[r][c] != src:
            return
        board[r][c] = dst
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            dfs(r + dr, c + dc, src, dst)

    for i in range(m):
        dfs(i, 0, "O", "#")
        dfs(i, n - 1, "O", "#")
    for j in range(n):
        dfs(0, j, "O", "#")
        dfs(m - 1, j, "O", "#")
    ans = 0
    for i in range(m):
        for j in range(n):
            if board[i][j] == "O":
                ans += 1
                dfs(i, j, "O", "X")
    return ans
```
