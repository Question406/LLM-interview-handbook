---
id: lc-130-surrounded-regions
section: graph
order: 2
level: A
title: LC 130 · 被围绕的区域
quick: >-
  从 outer edge 向内标记：从四条边上的 `'O'` 出发 DFS，把能到达 outer edge 的整片标成临时符，剩下没标到的 `'O'`
  一定被围住，改成 `'X'`，再把临时符改回 `'O'`。时间 $O(mn)$。
tags:
  - DFS
  - Grid
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 130. 被围绕的区域
    url: 'https://leetcode.cn/problems/surrounded-regions/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定只含字符 `X`、`O` 的矩形棋盘 `board`。上下左右相邻的 O 属于同一区域；如果一个区域的任何格子都不能通过连续的 O 到达 board boundaries，就认为它被包围。把所有被包围区域中的 O 改为 X；与 outer edge 连通的 O 保持不变，对角线不算连通。

### 输入与输出

实现 `solve(board) -> None`，直接原地更新传入的二维列表，不另返回新棋盘。示例“输出”展示的是调用结束后 board 的内容。

### 约束

- 棋盘为 m 行 n 列，`1 <= m, n <= 200`。
- 每个格子只可能是字符 `X` 或 `O`，不是数字0。

### 示例

```text
输入：board = [["X","X","X","X"],["X","O","O","X"],["X","X","O","X"],["X","O","X","X"]]
输出：[["X","X","X","X"],["X","X","X","X"],["X","X","X","X"],["X","O","X","X"]]
```

[LeetCode 原题](https://leetcode.com/problems/surrounded-regions/description/)

## 解题思路与参考答案

## 题意

$m\times n$ 棋盘由 `'X'` 和 `'O'` 组成。把所有被 `'X'` 四连通围住的 `'O'` 改成 `'X'`；能到达 outer edge 的 `'O'` 不算被围，保持原样。要求原地修改。

## 思路

我会从 outer edge 向内标记。被围住等价于无法到达 outer edge，所以从四条边上的 `'O'` 出发做 DFS 或 BFS，把与 outer edge 连通的整片标成临时符（比如 `'#'`）。然后扫一遍全盘：剩下的 `'O'` 一定被围住，改成 `'X'`；`'#'` 改回 `'O'`。

拿示例来说，第二、三行中间那片 `'O'` 到不了 outer edge，标记时不会被走到，第二遍扫盘时变成 `'X'`；最后一行那个 `'O'` 本身就在边上，被标成 `'#'`，最后恢复成 `'O'`。

从内部 `'O'` 出发再判断有没有碰到边，容易漏掉连通关系，也更慢。所以开口就说：先保留与 outer edge 相连的 cells，再翻内部。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
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
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$（递归栈）；每个格子只被标记常数次。

## Edge Cases

$1\times n$ 或 $m\times 1$ 时每个 cells 都位于 outer edge，`'O'` 全部保留，一个都不翻。整盘都是 `'O'` 时，从四边出发会把整盘标成 `'#'`，最后全部改回 `'O'`。内部有一块封闭区域时，从 outer edge 开始的 DFS 碰不到它，第二遍扫盘时改成 `'X'`。这题和「沉岛计数」是对偶的：本题保留与 outer edge 相连的 cells、翻内部，岛屿数量是把所有陆地淹掉，见 LC 200，独立卡 `lc-200-number-of-islands`。

## 追问

**「被围」改成八连通呢？**
标记 connected components touching the outer edge 时八个方向都走，包括对角线，内部翻盘仍只处理没被标记的 `'O'`。八连通下「围住」更难成立，对角也能漏出去，被围的区域会变少。

```python
DIRS8 = (
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
)


def markBorder8(board, r, c):
    m, n = len(board), len(board[0])
    if r < 0 or r >= m or c < 0 or c >= n or board[r][c] != "O":
        return
    board[r][c] = "#"
    for dr, dc in DIRS8:
        markBorder8(board, r + dr, c + dc)
```

**只统计被围区域有几块、不改盘呢？**
还是先从 outer edge `'O'` 出发，把能逃出去的整片标掉，然后对剩下的 `'O'` 跑一遍「沉岛」：每发现一块计数加一并淹掉。这就是把 LC 200 套在去掉 connected components touching the outer edge 之后的盘上。

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
