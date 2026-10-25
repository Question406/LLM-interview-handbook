---
id: lc-36-valid-sudoku
section: matrix
order: 1
level: A
title: LC 36 · 有效的数独
quick: "行、列、九宫各用一组集合，只检查已经填了的数字，同一单元里出现两次就非法。棋盘固定 $9\\times 9$，时间 $O(1)$。"
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

## 题目描述

给定一个已经部分填入数字的 9×9 数独盘，判断当前填入的数字是否满足规则：每一行、每一列以及九个互不重叠的 3×3 宫中，数字 1 到 9 均不能重复。只检查当前状态，不需要解出数独，也不需要判断它最终是否有解。

### 输入与输出

实现 `isValidSudoku(board) -> bool`。board 的元素是字符，"." 表示未填写。空格不参与重复判断，符合全部现有约束时返回 True。

### 约束与约定

- board 必须恰好有 9 行，每行恰好有 9 个字符。
- 每个字符为 "1" 到 "9" 或 "."。

### 示例

```text
输入：board =
[["5","3",".",".","7",".",".",".","."]
,["6",".",".","1","9","5",".",".","."]
,[".","9","8",".",".",".",".","6","."]
,["8",".",".",".","6",".",".",".","3"]
,["4",".",".","8",".","3",".",".","1"]
,["7",".",".",".","2",".",".",".","6"]
,[".","6",".",".",".",".","2","8","."]
,[".",".",".","4","1","9",".",".","5"]
,[".",".",".",".","8",".",".","7","9"]]
输出：true
```

示例所有已填入数字均未违反行、列或宫的规则，因此返回 true。

[官方原题与完整题面](https://leetcode.com/problems/valid-sudoku/description/)。

## 解题思路与参考答案

## 题意

$9\times 9$ 的数独盘，`.` 表示空格。只验证已经填入的数字在行、列、九宫内有没有冲突，不用判断有没有解。

## 思路

我先跟面试官确认这题不求解、只查冲突，然后用三组集合一遍扫完。`rows[i]`、`cols[j]`、`boxes[b]` 分别记行、列、九宫里出现过的数字，九宫下标是 $b=(i//3)\cdot 3+j//3$。扫到数字时，任一集合里已经有这个值就返回失败，否则加进去；空格跳过。

拿测试里的 `bad` 盘来说，左上角的 `"5"` 改成了 `"8"`。扫到第 2 行的那个 `"8"` 时，它和左上角在同一个九宫，`boxes[0]` 里已经有 8，直接返回 False。同一列下面第 3 行也还有一个 8，就算九宫没撞上，列也会查出来。

位掩码也能做。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
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
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

棋盘固定 $9\times 9$，时间、空间都是 $O(1)$。一般的 $n\times n$ 则是 $O(n^2)$。

## 边界

- 全空时没有冲突，算合法，这题不要求有解。
- 冲突只出现在某一行或者某个九宫时，对应的集合会查出来，另外两组可能仍然合法。
- 同一个数字出现在不同宫、不同行、不同列时，三组集合都不冲突，合法。

## 追问

**要求解数独（LC 37）呢？**
用回溯。先像这题一样维护行、列、宫的已用集合，收集所有空格，依次枚举 `'1'..'9'`，三处都不冲突就填入并递归，失败就撤销。可以先挑候选最少的空格（MRV）来加速。棋盘有解时回溯会把它填满；这题只验证，不保证有解。

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

**$n$ 更大呢？**
行、列、宫还是用哈希或者位集，扫描 $O(n^2)$。宫一般是 $b\times b$（$n=b^2$），下标是 `(i//b)*b + j//b`。只验证冲突仍然是线性扫一遍盘；求解的话，回溯分支会随 $n$ 指数爆炸，要用精确覆盖、舞蹈链这一类方法。
