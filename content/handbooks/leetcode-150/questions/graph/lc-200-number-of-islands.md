---
id: lc-200-number-of-islands
section: graph
order: 1
level: S
title: LC 200 · 岛屿数量
quick: >-
  扫网格，遇到 `'1'` 就说明发现一座新岛，计数加一，再用 DFS/BFS 把它四连通的陆地全改成 `'0'`（或记进 `visited`），之后不会重复计数。每个格子最多访问一次，时间 $O(mn)$。
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

## 题目描述

给定字符网格 grid，`"1"` 表示陆地，`"0"` 表示水。只要陆地格子能通过上下左右相邻的陆地互相到达，就属于同一座岛屿。网格边界外都视为水，求网格中共有多少座岛屿。

### 接口与输出

实现 `numIslands(grid: List[List[str]]) -> int`，返回岛屿数量。对角线接触不能连接两座岛，值必须按字符 "0"/"1" 理解。

### 合法输入与约束

网格矩形且非空，行数和列数均为 1 到 300，所有格子均为字符 "0" 或 "1"。全水网格的结果为 0。

### 示例

```text
输入：grid = [
  ["1","1","1","1","0"],
  ["1","1","0","1","0"],
  ["1","1","0","0","0"],
  ["0","0","0","0","0"]
]
输出：1
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/number-of-islands/description/)。

## 解题思路与参考答案

## 题意

$m\times n$ 网格，`'1'` 是陆地、`'0'` 是水。上下左右四连通的陆地算同一座岛，求岛屿个数。

## 思路

我会用「沉岛」的办法：从左上往右下扫每个格子，遇到 `'1'` 就说明碰到了一座还没数过的岛，计数加一，然后 DFS/BFS 把这整座岛淹掉，也就是把访问到的陆地改成 `'0'`。之后扫到这座岛的其他格子时，它们已经是水了，不会被重复计数。只走上下左右四个方向，斜对角不算相连。

拿代码里第二个例子看：左上角那块 2×2 的陆地，扫到 `(0,0)` 时计数变成 1，DFS 把四个格子都改成 `'0'`；接着扫到 `(2,2)` 这块孤立的陆地，计数变成 2；最后扫到右下角 `(3,3)`、`(3,4)` 这一对，计数变成 3。

另开一个 `visited` 数组效果一样，改原网格只是省空间。白板上我先讲沉岛，再补一句并查集也能做：每个 `'1'` 和它的四邻合并，最后数有多少个根。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
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
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，每个格子最多进一次 DFS。额外空间最坏 $O(mn)$，整张图都是陆地时递归栈会这么深。

## 边界

全是水的话一次 DFS 都不进，答案是 $0$；全是陆地的话第一次沉岛就把整盘淹掉，答案是 $1$。单格 `'1'` 答案是 $1$，单格 `'0'` 答案是 $0$。两座岛只在斜对角相邻时，四连通下仍然算两座。

被围区域那种「保留边界、翻转内部」的题是 LC 130，单独一张卡 `lc-130-surrounded-regions`。

## 追问

**改成八连通，或者不能改原网格呢？**
八连通就是多走四条对角线，其余不变。不能改盘就另开 `visited`，访问时就标记，效果和改成 `'0'` 一样。

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

**最大面积（LC 695）或者周长（LC 463）怎么做？**
沉岛的时候顺手累加就行，格子照样改。面积让 DFS 返回这次连通的 `'1'` 个数，全局取 max。周长是每个陆地格子先算 $4$，每有一条和上邻居或左邻居共享的边就减 $2$；只看上和左，每条共享边只处理一次，不会因为两边各减一次而算错。

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
