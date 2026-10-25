---
id: lc-994-rotting-oranges
section: graph-bfs
order: 2
level: S
title: LC 994 · 腐烂的橘子
quick: "用多源 BFS：所有烂橘子一起作为第 $0$ 层入队，一层就是一分钟，同时数新鲜橘子。BFS 结束后还有新鲜的就返回 $-1$，否则返回层数。时间 $O(mn)$，额外空间 $O(mn)$。"
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
  - title: 994. Rotting Oranges
    url: https://leetcode.com/problems/rotting-oranges/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定一个网格，0 表示空格，1 表示新鲜橘子，2 表示已经腐烂的橘子。每经过一分钟，所有腐烂橘子会同时使其上下左右紧邻的新鲜橘子腐烂；对角线不算相邻，空格也不会传播腐烂。求让所有橘子都腐烂所需的最少分钟数。

### 输入与输出

实现 `orangesRotting(grid: List[List[int]]) -> int`。若仍有橘子永远无法腐烂，返回 -1；初始就没有新鲜橘子时返回 0。每一分钟的感染是同时发生的，新感染的位置要到下一分钟才能继续向外传播。

### 约束

- 网格为 m 行 n 列，`1 <= m,n <= 10`。
- 每个格子的值只可能是 0、1、2。

### 示例

```text
输入：grid = [[2,1,1],[1,1,0],[0,1,1]]
输出：4
```

## 解题思路与参考答案

## 题意

$m\times n$ 网格，$0$ 空、$1$ 新鲜橘子、$2$ 烂橘子。每过一分钟，烂橘子上下左右相邻的新鲜橘子都会变烂。返回所有橘子都烂掉所需的最少分钟数；不可能则返回 $-1$。

## 思路

我用多源 BFS，因为每个新鲜橘子变烂的时间，就是它到最近烂橘子的网格距离。把所有初始烂橘子一起放进队列当第 $0$ 层，BFS 每扩一层算一分钟，这样每个格子第一次被访问时的层数，就是它到最近源的距离。

开始时先数一下新鲜橘子 `fresh`，每烂一个减一。BFS 结束后 `fresh` 还大于 $0$，说明有橘子被隔开了，返回 $-1$。循环条件里带上 `fresh`，只在还有新鲜橘子时才扩下一层，免得最后一层空扩多算一分钟。

拿 `[[2,1,1],[1,1,0],[0,1,1]]` 看：左上角的烂橘子第 1 分钟烂掉右边和下面两个，第 2 分钟再往外一圈，到第 4 分钟右下角那个才烂，答案 4。

容易想到的另一种做法是对每个烂橘子单独跑 BFS 再取最小值，烂橘子多的时候是 $O(k\cdot mn)$。多源一起入队只要跑一次。

## 参考代码

```python
from collections import deque
from typing import List


def orangesRotting(grid: List[List[int]]) -> int:
    m, n = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 2:
                q.append((r, c))
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while q and fresh:
        for _ in range(len(q)):
            r, c = q.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                    grid[nr][nc] = 2
                    fresh -= 1
                    q.append((nr, nc))
        minutes += 1
    return -1 if fresh else minutes


if __name__ == "__main__":
    assert orangesRotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
    assert orangesRotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
    assert orangesRotting([[0, 2]]) == 0
    assert orangesRotting([[0]]) == 0
    assert orangesRotting([[1]]) == -1
    assert orangesRotting([[2, 1, 1, 1, 2]]) == 2
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert orangesRotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
assert orangesRotting([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
assert orangesRotting([[0, 2]]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，每个格子最多入队一次。额外空间 $O(mn)$，最坏整张网格都在队列里。

## 边界

一开始就没有新鲜橘子时返回 $0$，哪怕也没有烂橘子。

有新鲜橘子但没有烂橘子时，循环不进，`fresh` 大于 $0$，返回 $-1$。

两端各有一个烂橘子往中间扩时，多源同时推进，每个橘子的时间是到最近那个源的距离，比如 `[[2,1,1,1,2]]` 两分钟就全烂了。

## 追问

**不能改输入怎么办？**
另开一个 `dist` 矩阵或 `seen` 集合记录已经烂掉的格子，逻辑一样，空间还是 $O(mn)$。

**要每个橘子变烂的具体时间呢？**
用 `dist[r][c]` 记录入队时的层数，就是多源最短距离。它和 `lc-1926-nearest-exit-from-entrance-in-maze` 都是网格上的无权最短路，这题的源有多个。

```python
from collections import deque

def rotTimes(grid):
    m, n = len(grid), len(grid[0])
    dist = [[-1] * n for _ in range(m)]
    q = deque()
    for r in range(m):
        for c in range(n):
            if grid[r][c] == 2:
                dist[r][c] = 0
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1 and dist[nr][nc] == -1:
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist
```
