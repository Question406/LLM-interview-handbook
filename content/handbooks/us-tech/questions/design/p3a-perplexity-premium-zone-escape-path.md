---
id: p3a-perplexity-premium-zone-escape-path
section: design
order: 608
level: A
title: "Perplexity：地理区域逃离：黑盒判定与搜索假设"
quick: "先问清区域是否连通或凸、有没有道路约束、搜索空间的边界和分辨率；离散成有限网格后，从起点 BFS 找到的第一个非 premium 格就是最近的出口。"
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · premium-zone-escape-path"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/premium-zone-escape-path
    type: secondary
---

## 题目

给一个起点坐标和一个黑盒函数，函数能判断某个位置是否在 premium zone 里。要求找出一个不在 premium zone 内的坐标，或者给出一条从起点走出去的路径。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。原帖没有给出地理坐标怎么离散化、边界在哪里，下面的网格版本、接口和测试是手册补的练习约定，不是原题。

## 思路

这道题的题面信息不够，最重要的一步是先问清假设，再选算法：

- 区域是否连通、是不是凸的？凸区域可以沿任意方向一直走直到出去，非凸区域可能需要绕路。
- 移动有没有道路约束，能不能穿过禁区？
- 搜索空间有没有边界、按什么分辨率离散化？要求的是最短路径，还是任意一个外部点？

如果把空间离散成有限网格，可以从起点做 BFS，第一个碰到的非 premium 格就是最近的出口。但如果没有边界或分辨率，BFS 可能永远不会结束，也谈不上最优。所以不要直接把它当成普通的二维迷宫来做，要把用到的假设讲出来。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `escape(rows, cols, start, is_premium)`：在 `rows × cols` 的有限网格上，从 `start` 出发四邻接移动，不能越界。返回到任意一个非 premium 格的最短路径，坐标列表包含起点和终点。
- `is_premium((r, c))` 是纯函数。起点本身不是 premium 时返回 `[start]`；整个可达区域都是 premium 时返回 `None`。
- 网格为空或起点不在网格内时抛 `ValueError`。网格不超过 300 × 300。
- 这个网格约定只是把题目变得可判定，不代表真实地图题的唯一答案。

### 输入输出示例

```text
escape(3, 3, (1, 1), is_premium=lambda cell: cell == (1, 1))
  -> [(1, 1), (0, 1)]    # 中心一步走到上方的邻格
escape(2, 2, (0, 0), is_premium=lambda cell: True)   -> None
escape(2, 2, (0, 0), is_premium=lambda cell: False)  -> [(0, 0)]
```

### 解题思路与正确性

BFS 按离起点的步数从小到大出队，所以第一个出队的非 premium 格离起点最近，回溯得到的路径就是最短的。

`prev` 在入队时就写入，同时充当 visited 集合，每个格子最多入队一次，也最多调用一次 `is_premium`。`prev` 记录了每个格子是从哪里走过来的，所以能还原出完整路径，而不只是终点。网格有限，所以即使不存在出口，搜索也会在遍历完所有可达格子后结束，返回 `None`。

### 完整参考实现（Python 3）

```python
from collections import deque

# 固定的邻居顺序：上、左、右、下，保证结果确定
NEIGHBOR_STEPS = ((-1, 0), (0, -1), (0, 1), (1, 0))


def escape(rows, cols, start, is_premium):
    """在 rows x cols 网格上从 start 出发四邻接移动，返回到最近的非 premium 格的最短路径。

    路径包含起点和终点；起点本身不是 premium 时返回 [start]；整个网格都是 premium 时返回 None。
    """
    if rows < 1 or cols < 1:
        raise ValueError(f"grid must be non-empty, got {rows}x{cols}")
    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        raise ValueError(f"start {start} is outside the grid")

    queue = deque([start])
    prev = {start: None}  # 兼作 visited：入队时就记录，避免同一格重复入队
    while queue:
        cell = queue.popleft()
        if not is_premium(cell):
            return rebuild_path(prev, cell)
        row, col = cell
        for d_row, d_col in NEIGHBOR_STEPS:
            neighbor = (row + d_row, col + d_col)
            inside = 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols
            if inside and neighbor not in prev:
                prev[neighbor] = cell
                queue.append(neighbor)
    return None


def rebuild_path(prev, end):
    path = []
    cell = end
    while cell is not None:
        path.append(cell)
        cell = prev[cell]
    return path[::-1]
```

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 只有中心是 premium，一步就能出去
path = escape(3, 3, (1, 1), lambda cell: cell == (1, 1))
assert len(path) == 2
assert path[0] == (1, 1)

# 整个网格都是 premium
assert escape(2, 2, (0, 0), lambda cell: True) is None

# 起点已经在外面
assert escape(2, 2, (0, 0), lambda cell: False) == [(0, 0)]

# 最短路径：只有最右一列在外面，从 (1, 0) 出发要走 3 步
path = escape(3, 4, (1, 0), lambda cell: cell[1] < 3)
assert len(path) == 4
assert path[-1][1] == 3

expect_value_error(escape, 0, 3, (0, 0), lambda cell: True)
expect_value_error(escape, 2, 2, (2, 0), lambda cell: True)
```

### 复杂度与追问

设网格有 $R \times C$ 个格子。最坏情况下每个格子调用一次 `is_premium`，时间和空间都是 O(RC)。

如果追问 `is_premium` 很贵（比如要调远程服务）：BFS 已经保证每个格子最多查一次；还可以在结果里缓存，或者先沿几个方向以倍增步长探测，找到外部点后再在边界附近细化。

如果追问真实地图：经纬度是连续空间，要先定好道路网络、尺度、可达性和停止条件。只有一个黑盒的区域判定函数，无法保证对任意形状的区域都能找到最短的逃离路径。
