---
id: lc-36-valid-sudoku
section: matrix
order: 1
level: A
title: LC 36 · 有效的数独
quick: >-
  行、列、九宫各用一个集合。只检查已填数字，同一单元出现两次即非法。棋盘固定 $9\times 9$，时间
  $O(1)$。
tags:
  - Hash
  - Matrix
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 36. 有效的数独
    url: https://leetcode.cn/problems/valid-sudoku/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$9\times 9$ 数独盘，`.` 表示空格。只验证已经填入的数字是否在行、列、九宫内互不冲突，不必判断是否有解。

## 思路

三组集合：`rows[i]`、`cols[j]`、`boxes[b]`。九宫下标 $b=(i//3)\cdot 3+j//3$。扫到数字时，任一集合已含该值就失败，否则加入。空格跳过。

位掩码也能做。我会先声明「不求解，只查冲突」。

## 参考代码

```python
from typing import List


def isValidSudoku(board: List[List[str]]) -> bool:
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for i in range(9):
        for j in range(9):
            c = board[i][j]
            if c == ".":
                continue
            b = (i // 3) * 3 + j // 3
            if c in rows[i] or c in cols[j] or c in boxes[b]:
                return False
            rows[i].add(c)
            cols[j].add(c)
            boxes[b].add(c)
    return True


if __name__ == "__main__":
    ok = [
        ["5", "3", ".", ".", "7", ".", ".", ".", "."],
        ["6", ".", ".", "1", "9", "5", ".", ".", "."],
        [".", "9", "8", ".", ".", ".", ".", "6", "."],
        ["8", ".", ".", ".", "6", ".", ".", ".", "3"],
        ["4", ".", ".", "8", ".", "3", ".", ".", "1"],
        ["7", ".", ".", ".", "2", ".", ".", ".", "6"],
        [".", "6", ".", ".", ".", ".", "2", "8", "."],
        [".", ".", ".", "4", "1", "9", ".", ".", "5"],
        [".", ".", ".", ".", "8", ".", ".", "7", "9"],
    ]
    bad = [row[:] for row in ok]
    bad[0][0] = "8"
    assert isValidSudoku(ok) is True
    assert isValidSudoku(bad) is False
    print("ok")
```

## 复杂度

棋盘固定 $9\times 9$，时间、空间都是 $O(1)$。一般 $n\times n$ 则 $O(n^2)$。

## 边界

- 全空：没有冲突，合法；这题不要求有解。
- 只有一行冲突 / 只在九宫冲突：对应集合会检出，另外两组可能仍合法。
- 同一数字出现在不同宫且不同行列：三组集合都不冲突，合法。

## 追问

- **求解数独（LC 37）？** 先用这题方式维护行/列/宫已用集合。收集空格，依次枚举 `'1'..'9'`，三处都不冲突则填入并递归，失败则撤销。可先挑候选最少的空格（MRV）加速。棋盘有解则回溯会填满；这题只验证，不保证有解。

```python
def solveSudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empties = []
    for i in range(9):
        for j in range(9):
            c = board[i][j]
            if c == ".":
                empties.append((i, j))
            else:
                rows[i].add(c)
                cols[j].add(c)
                boxes[(i // 3) * 3 + j // 3].add(c)

    def dfs(k):
        if k == len(empties):
            return True
        i, j = empties[k]
        b = (i // 3) * 3 + j // 3
        for c in "123456789":
            if c in rows[i] or c in cols[j] or c in boxes[b]:
                continue
            board[i][j] = c
            rows[i].add(c)
            cols[j].add(c)
            boxes[b].add(c)
            if dfs(k + 1):
                return True
            rows[i].remove(c)
            cols[j].remove(c)
            boxes[b].remove(c)
            board[i][j] = "."
        return False

    dfs(0)
```

- **$n$ 更大？** 行/列/宫仍用哈希或位集，扫描 $O(n^2)$。宫一般是 $b\times b$（$n=b^2$），下标 `(i//b)*b + j//b`。只验证冲突仍是线性扫盘；求解则回溯分支随 $n$ 指数爆炸，需要精确覆盖 / 舞蹈链一类。
