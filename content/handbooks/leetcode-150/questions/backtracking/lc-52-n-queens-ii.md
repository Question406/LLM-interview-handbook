---
id: lc-52-n-queens-ii
section: backtracking
order: 5
level: A
title: LC 52 · N 皇后 II
quick: "按行放皇后；尝试位置 $(r,c)$ 时，检查列、主对角 $r-c$ 和副对角 $r+c$ 是否已被占用。合法就递归下一行，返回时撤销。放完第 $n$ 行，方案数加一。"
tags:
  - Backtracking
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 52. N 皇后 II
    url: https://leetcode.cn/problems/n-queens-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$n$ 皇后：在 $n\times n$ 棋盘放 $n$ 个皇后，彼此不能同行、同列、同对角线。返回合法摆法的数量（不需要棋盘图案）。

## 思路

一行放一个。到第 $r$ 行时枚举列 $c$，若列、主对角 `r-c`、副对角 `r+c` 任一被占则跳。放下后递归 $r+1$，回来撤销。$r=n$ 计数加一。

只需个数，不必构造字符串棋盘。$n\le 9$ 可用三个位掩码代替集合。三个约束（列、主对角、副对角）先说清楚，再写回溯。

## 参考代码

```python
def totalNQueens(n: int) -> int:
    cols = set()
    diag = set()
    antidiag = set()
    ans = 0

    def dfs(r: int) -> None:
        nonlocal ans
        if r == n:
            ans += 1
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in antidiag:
                continue
            cols.add(c)
            diag.add(r - c)
            antidiag.add(r + c)
            dfs(r + 1)
            cols.remove(c)
            diag.remove(r - c)
            antidiag.remove(r + c)

    dfs(0)
    return ans


if __name__ == "__main__":
    assert totalNQueens(4) == 2
    assert totalNQueens(1) == 1
    print("ok")
```

## 复杂度

时间 $O(n!)$ 量级（每行剪枝后少于 $n$ 个选择）。额外空间 $O(n)$。

## 边界

- $n=1$：答案 $1$（独皇后占唯一格）。
- $n=2,3$：列与对角互相卡住，无解，返回 $0$。
- $n=4$：恰好 $2$ 种，可手算验证回溯。

## 追问

- **要输出棋盘图案（LC 51）？** 计数改成构造。路径记下每行放的列 `cols[r]=c`，或直接在 `board[r][c]` 写 `'Q'`。$r=n$ 时把每行 `"".join` 拷进答案，再回溯恢复 `'.'`。约束与本题完全相同：列、`r-c`、`r+c`。

```python
def solveNQueens(n):
    board = [["."] * n for _ in range(n)]
    cols, diag, antidiag = set(), set(), set()
    ans = []

    def dfs(r):
        if r == n:
            ans.append(["".join(row) for row in board])
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in antidiag:
                continue
            cols.add(c)
            diag.add(r - c)
            antidiag.add(r + c)
            board[r][c] = "Q"
            dfs(r + 1)
            board[r][c] = "."
            cols.remove(c)
            diag.remove(r - c)
            antidiag.remove(r + c)

    dfs(0)
    return ans
```

- **位运算加速？** $n\le 9$，用三个整型掩码代替集合。`cols` 第 $c$ 位表示列占用；主对角每次下行把掩码左移一位，副对角右移一位。`avail = ((1 << n) - 1) & ~(cols | diag | antidiag)` 取出可放列，`bit = avail & -avail` 取最低位 1，放下后递归。

```python
def totalNQueensBits(n):
    ans = 0

    def dfs(r, cols, diag, antidiag):
        nonlocal ans
        if r == n:
            ans += 1
            return
        avail = ((1 << n) - 1) & ~(cols | diag | antidiag)
        while avail:
            bit = avail & -avail
            avail -= bit
            dfs(r + 1, cols | bit, (diag | bit) << 1, (antidiag | bit) >> 1)

    dfs(0, 0, 0, 0)
    return ans
```

- **数独求解（LC 37）？** 同一套「选位置 + 约束集合 + 回溯」。空格枚举 $1..9$，行 / 列 / 九宫不能重复；可先填约束最多的格剪枝。只验证已填数字见 LC 36，独立卡 `lc-36-valid-sudoku`（不必搜解）。

```python
def solveSudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    box = [set() for _ in range(9)]
    empty = []
    for r in range(9):
        for c in range(9):
            if board[r][c] == ".":
                empty.append((r, c))
            else:
                v = board[r][c]
                rows[r].add(v)
                cols[c].add(v)
                box[(r // 3) * 3 + c // 3].add(v)

    def dfs(i):
        if i == len(empty):
            return True
        r, c = empty[i]
        b = (r // 3) * 3 + c // 3
        for v in "123456789":
            if v in rows[r] or v in cols[c] or v in box[b]:
                continue
            board[r][c] = v
            rows[r].add(v)
            cols[c].add(v)
            box[b].add(v)
            if dfs(i + 1):
                return True
            board[r][c] = "."
            rows[r].discard(v)
            cols[c].discard(v)
            box[b].discard(v)
        return False

    dfs(0)
```
