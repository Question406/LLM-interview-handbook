---
id: lc-52-n-queens-ii
section: backtracking
order: 5
level: A
title: LC 52 · N 皇后 II
quick: >-
  一行放一个皇后，尝试 $(r,c)$ 时检查列、主对角 $r-c$、副对角 $r+c$ 有没有被占。合法就递归下一行，回来撤销；放完第 $n$
  行方案数加一。只要个数，不用构造棋盘。
tags:
  - Backtracking
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 52. N 皇后 II
    url: 'https://leetcode.cn/problems/n-queens-ii/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

在一个 n×n 的棋盘上放置 n 个皇后。任意两个皇后不能处于同一行、同一列或同一条斜线上；两种摆放只要有某个格子是否放皇后不同，就算不同方案。求满足条件的摆放方案总数。

### 接口与输出

实现 `totalNQueens(n: int) -> int`。只返回方案数量，不需要输出棋盘图案或皇后坐标。

### 合法输入与约束

`1 <= n <= 9`。没有合法摆法时返回 0；不能只统计旋转或镜像后视为相同的代表方案。

### 示例

```text
输入：n = 4
输出：2
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/n-queens-ii/description/)。

## 解题思路与参考答案

## 题意

$n$ 皇后：在 $n\times n$ 棋盘放 $n$ 个皇后，彼此不能同行、同列、同对角线。返回合法摆法的数量（不需要棋盘图案）。

## 思路

我会按行回溯，一行放一个，这样同行自动满足，只剩三个约束：列、主对角 `r-c`、副对角 `r+c`。到第 $r$ 行时枚举列 $c$，三者任一被占就跳过；放下后递归 $r+1$，回来撤销；$r=n$ 时计数加一。

用 `r-c` 和 `r+c` 是因为同一条主对角线上 $r-c$ 相同，同一条副对角线上 $r+c$ 相同。比如 $(0,1)$ 和 $(1,2)$ 的 $r-c$ 都是 $-1$，在同一条主对角线上，放了前一个，后一个就会被挡掉。

题目只要个数，不必构造字符串棋盘。$n\le 9$ 时可以用三个 bitmask 代替集合。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert totalNQueens(4) == 2
assert totalNQueens(1) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间是 $O(n!)$ 量级，每行剪枝后少于 $n$ 个选择；额外空间 $O(n)$。

## Edge Cases

$n=1$ 时答案是 $1$，一个皇后占唯一的格子。$n=2,3$ 时列和对角互相卡住，无解，返回 $0$。$n=4$ 恰好 $2$ 种，可以手算验证回溯。

## 追问

**要输出棋盘图案（LC 51）呢？**
把计数改成构造，约束和本题完全一样，还是列、`r-c`、`r+c`。路径记下每行放的列 `cols[r]=c`，或者直接在 `board[r][c]` 写 `'Q'`；$r=n$ 时把每行 `"".join` 拷进答案，回溯时恢复 `'.'`。

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

**能用位运算加速吗？**
可以，$n\le 9$ 时用三个整型 mask 代替集合。`cols` 第 $c$ 位表示这一列被占；往下走一行，主对角 mask 左移一位，副对角 mask 右移一位。`avail = ((1 << n) - 1) & ~(cols | diag | antidiag)` 取出可放的列，`bit = avail & -avail` 取最低位的 1，放下后递归。

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

**数独求解（LC 37）也是这个套路吗？**
是，同一套「选位置 + 约束集合 + 回溯」。每个空格枚举 $1..9$，行、列、九宫里不能重复；先填约束最多的格子可以剪枝。只验证已填数字、不用搜解的是 LC 36，独立卡 `lc-36-valid-sudoku`。

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
