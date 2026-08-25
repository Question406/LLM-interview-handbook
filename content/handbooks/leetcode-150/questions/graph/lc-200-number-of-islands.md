---
id: lc-200-number-of-islands
section: graph
order: 1
level: S
title: LC 200 · 岛屿数量
quick: >-
  网格 `'1'` 是陆地。扫到一块就 DFS/BFS 把四连通全改成 `'0'`（或 `visited`），块数加一。时间
  $O(mn)$。
tags:
  - DFS
  - Grid
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 200. 岛屿数量
    url: https://leetcode.cn/problems/number-of-islands/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$m\times n$ 网格，`'1'` 陆地、`'0'` 水。四连通（上下左右）的陆地算同一座岛。求岛屿个数。

## 思路

扫每个格子。遇到 `'1'` 说明发现新岛，计数加一，再 DFS/BFS 把整座岛淹掉：访问过的陆地改成 `'0'`，避免重复计数。只走四连通，斜对角不算。

另开 `visited` 等价，但改原网格省空间。白板我先讲「沉岛」，再补并查集：`'1'` 与四邻合并，最后数连通块。

## 参考代码

```python
from typing import List


def numIslands(grid: List[List[str]]) -> int:
    if not grid:
        return 0
    m, n = len(grid), len(grid[0])

    def dfs(r: int, c: int) -> None:
        if r < 0 or r >= m or c < 0 or c >= n or grid[r][c] != "1":
            return
        grid[r][c] = "0"
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    ans = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1":
                ans += 1
                dfs(i, j)
    return ans


if __name__ == "__main__":
    g1 = [
        ["1", "1", "1", "1", "0"],
        ["1", "1", "0", "1", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "0", "0", "0"],
    ]
    assert numIslands(g1) == 1
    g2 = [
        ["1", "1", "0", "0", "0"],
        ["1", "1", "0", "0", "0"],
        ["0", "0", "1", "0", "0"],
        ["0", "0", "0", "1", "1"],
    ]
    assert numIslands(g2) == 3
    print("ok")
```

## 复杂度

时间 $O(mn)$，每个格子进 DFS 至多一次。额外空间 $O(mn)$（递归栈最坏整图是陆地）。

## 边界

- 全水：一次都不进 DFS，答案 $0$；全陆：第一次沉岛把整盘淹掉，答案 $1$。
- 单格 `'1'` / `'0'`：答案 $1$ / $0$。
- 两岛仅斜对角相邻：四连通下仍是两座。被围区域（保边界翻内部）见 LC 130，独立卡 `lc-130-surrounded-regions`。

## 追问

- **改成八连通？不能改原网格？** 八连通再走四条对角线，其余不变。不能改盘就另开 `visited`，入栈时标记，语义与改 `'0'` 相同。

```python
DIRS8 = (
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
)

def numIslands8(grid):
    m, n = len(grid), len(grid[0])
    seen = [[False] * n for _ in range(m)]

    def dfs(r, c):
        if r < 0 or r >= m or c < 0 or c >= n:
            return
        if seen[r][c] or grid[r][c] != "1":
            return
        seen[r][c] = True
        for dr, dc in DIRS8:
            dfs(r + dr, c + dc)

    ans = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1" and not seen[i][j]:
                ans += 1
                dfs(i, j)
    return ans
```

- **最大面积（LC 695）/ 周长（LC 463）？** 沉岛时不要只改格子，顺手累加。面积：DFS 返回连通 `'1'` 个数，全局取 max。周长：每个陆地格子贡献 $4$，每有一条与上/左邻居的共享边减 $2$（避免双边各减一次漏计）。

```python
def maxAreaOfIsland(grid):
    m, n = len(grid), len(grid[0])

    def dfs(r, c):
        if r < 0 or r >= m or c < 0 or c >= n or grid[r][c] != 1:
            return 0
        grid[r][c] = 0
        return 1 + dfs(r + 1, c) + dfs(r - 1, c) + dfs(r, c + 1) + dfs(r, c - 1)

    return max((dfs(i, j) for i in range(m) for j in range(n)), default=0)


def islandPerimeter(grid):
    peri = 0
    m, n = len(grid), len(grid[0])
    for i in range(m):
        for j in range(n):
            if grid[i][j] != 1:
                continue
            peri += 4
            if i and grid[i - 1][j] == 1:
                peri -= 2
            if j and grid[i][j - 1] == 1:
                peri -= 2
    return peri
```
