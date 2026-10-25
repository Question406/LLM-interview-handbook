---
id: p3a-perplexity-premium-zone-escape-path
section: design
order: 608
level: A
title: "Perplexity：地理区域逃离：黑盒判定与搜索假设"
quick: "先确认地图边界、分辨率、道路约束，以及区域是否连通或凸，再决定怎么搜。若约定为有限网格、四邻接移动，就从起点 BFS，第一次找到的非 premium 格对应最短逃离路径。"
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

## 题目描述

一个有限网格中有 premium 和 non-premium 单元格。只能调用给定判断函数，寻找从起点离开 premium 区域的最短路径。

以下接口、边界和规模限制是手册重构的练习约定，不代表面试原题逐字原文；输入默认满足所列合法约束。

### 接口与规则

- `escape(rows, cols, start, is_premium)`：在 `rows × cols` 的有限网格上，从 `start` 出发四邻接移动，不能越界。返回到任意一个非 premium 格的最短路径，坐标列表包含起点和终点。
- `is_premium((r, c))` 是纯函数。起点本身不是 premium 时返回 `[start]`；整个可达区域都是 premium 时返回 `None`。
- `rows`、`cols` 为正整数，坐标为从 0 开始的 `(r,c)`，起点合法。若有多条最短路径，返回任意一条。网格不超过 300 × 300。
- 这个网格约定只是把题目变得可判定，不代表真实地图题的唯一答案。

### 输入输出示例

```text
escape(3, 3, (1, 1), is_premium=lambda cell: cell == (1, 1))
  -> [(1, 1), (0, 1)]    # 中心一步走到上方的邻格
escape(2, 2, (0, 0), is_premium=lambda cell: True)   -> None
escape(2, 2, (0, 0), is_premium=lambda cell: False)  -> [(0, 0)]
```

## 解题思路与参考答案

## 题目

给一个起点坐标和一个黑盒函数，函数能判断某个位置是否在 premium zone 里。要求找出一个不在 premium zone 内的坐标，或者给出一条从起点走出去的路径。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。原帖没有给出地理坐标怎么离散化、边界在哪里，下面的网格版本、接口和测试是手册补的练习约定，不是原题。

## 思路

如果题目约定有限网格和四邻接移动，我会用 BFS 找最近的非 premium 格，并用前驱记录还原路径。这个结论依赖空间离散且有界，动手前要先确认题目是否满足这些条件。

具体要问区域是否连通、是不是凸的，移动是否受道路约束、能否穿过禁区，以及空间边界和离散分辨率。还要确认目标是任意外部坐标，还是最短路径。凸区域可以沿任意方向一直走到外面，非凸区域可能需要绕路。

下面按有限网格实现。若没有边界或分辨率，BFS 可能无法结束，也不能直接宣称找到了最优路径。

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

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert len(path) == 2` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

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
