---
id: lc-1926-nearest-exit-from-entrance-in-maze
section: graph-bfs
order: 1
level: A
title: LC 1926 · 迷宫中离入口最近的出口
quick: "这是网格上的无权最短路，从入口 BFS，第一次扩展到的边界空格就是最近出口，入口本身不算。时间 $O(mn)$，额外空间 $O(mn)$。"
tags:
  - Graph
  - BFS
  - Matrix
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1926. Nearest Exit from Entrance in Maze
    url: https://leetcode.com/problems/nearest-exit-from-entrance-in-maze/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定矩形迷宫 `maze` 与入口坐标 `entrance=[row,col]`。字符 `.` 表示可通行格，`+` 表示墙；每一步只能向上下左右移动一格，不能穿墙或走出矩阵。出口是位于矩阵最外一行或最外一列的可通行格，但入口本身即使在边界上也不算出口。

### 输入与输出

实现 `nearestExit(maze, entrance) -> int`，返回从入口到任意出口所需的最少移动步数，不存在可达出口时返回 -1。入口到自身是0步，但不能因此把位于边界的入口判作出口。坐标从0开始。

### 约束

- 迷宫有 m 行 n 列，`1 <= m, n <= 100`。
- 格子只包含字符 `.` 或 `+`。
- entrance 恰有两个整数，均为有效行列下标，入口保证为空格。

### 示例

```text
输入：maze = [["+","+",".","+"],[".",".",".","+"],["+","+","+","."]], entrance = [1,2]
输出：1
```

[LeetCode 原题](https://leetcode.com/problems/nearest-exit-from-entrance-in-maze/description/)

## 解题思路与参考答案

## 题意

$m\times n$ 迷宫，`'.'` 是空格，`'+'` 是墙。从 `entrance = [r, c]`（保证是空格）出发，每步上下左右走一格，不能穿墙、不能出界。出口是位于边界上的空格，但入口自己不算出口。返回到最近出口的步数，没有则返回 $-1$。

## 思路

我用 BFS，因为每步代价都是 $1$，最短步数就是 BFS 的层数。入口先入队，一层层往外扩，第一次扩展到的边界空格一定最近，直接返回。

拿第一个样例看：入口在 `[1, 2]`，它正上方的 `[0, 2]` 是空格，而且在第一行边界上，扩展第一层就碰到它，答案是 1。

格子在入队时就标记已访问。拖到出队才标的话，同一格会被好几个邻居重复入队。判断出口放在扩展邻居这一步做，这样入口就算在边界上也不会被误判，因为入口是起点，从来不会作为邻居被检查。

DFS 能找到某个出口，但要找最短的那个就得枚举所有路径，是指数级。

## 参考代码

```python
from collections import deque
from typing import List


def nearestExit(maze: List[List[str]], entrance: List[int]) -> int:
    m, n = len(maze), len(maze[0])
    r0, c0 = entrance
    seen = [[False] * n for _ in range(m)]
    seen[r0][c0] = True
    q = deque([(r0, c0, 0)])
    while q:
        r, c, d = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < m and 0 <= nc < n):
                continue
            if maze[nr][nc] != "." or seen[nr][nc]:
                continue
            if nr in (0, m - 1) or nc in (0, n - 1):
                return d + 1
            seen[nr][nc] = True
            q.append((nr, nc, d + 1))
    return -1


if __name__ == "__main__":
    maze = [["+", "+", ".", "+"], [".", ".", ".", "+"], ["+", "+", "+", "."]]
    assert nearestExit(maze, [1, 2]) == 1
    maze = [["+", "+", "+"], [".", ".", "."], ["+", "+", "+"]]
    assert nearestExit(maze, [1, 0]) == 2
    assert nearestExit([[".", "+"]], [0, 0]) == -1
    assert nearestExit([["."]], [0, 0]) == -1
    maze = [["+", ".", "+"], ["+", ".", "+"], ["+", "+", "+"]]
    assert nearestExit(maze, [1, 1]) == 1
    maze = [["+", "+", "+"], ["+", ".", "+"], ["+", "+", "+"]]
    assert nearestExit(maze, [1, 1]) == -1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
maze = [["+", "+", ".", "+"], [".", ".", ".", "+"], ["+", "+", "+", "."]]
assert nearestExit(maze, [1, 2]) == 1
maze = [["+", "+", "+"], [".", ".", "."], ["+", "+", "+"]]
assert nearestExit(maze, [1, 0]) == 2
assert nearestExit([[".", "+"]], [0, 0]) == -1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，每个格子最多入队一次。额外空间 $O(mn)$，是 `seen` 和队列。

## 边界

入口在边界上时它不算出口，要找别的边界空格；代码只在邻居上判断出口，天然满足这一点。

只有入口一个空格，比如 `[["."]]`，没有出口，返回 $-1$。

入口被墙围死时，队列耗尽返回 $-1$。

## 追问

**要输出最短路径本身呢？**
BFS 时给每个格子记前驱 `parent[(nr, nc)] = (r, c)`，找到出口后沿着前驱回溯到入口，再反转。复杂度不变。

**有多个入口，问任一入口到任一出口的最短距离呢？**
用多源 BFS：所有入口一起作为第 $0$ 层入队，其余逻辑不变。`lc-994-rotting-oranges` 用的是同一种多源写法。

```python
from collections import deque

def nearestExitMulti(maze, entrances):
    m, n = len(maze), len(maze[0])
    starts = {tuple(e) for e in entrances}
    seen = set(starts)
    q = deque((r, c, 0) for r, c in starts)
    while q:
        r, c, d = q.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < m and 0 <= nc < n and maze[nr][nc] == "." and (nr, nc) not in seen:
                if (nr in (0, m - 1) or nc in (0, n - 1)) and (nr, nc) not in starts:
                    return d + 1
                seen.add((nr, nc))
                q.append((nr, nc, d + 1))
    return -1
```
