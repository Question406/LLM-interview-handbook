---
id: meta-maze-keys-direction-state
section: meta
order: 920
level: A
title: "Meta AI Coding：修复 maze solver，支持 keys、doors 与方向格"
quick: "我会先把 visited 从坐标改成坐标加 key mask。比如第一次经过门口没有 key，之后拿到 key 再回来，这两个状态能够继续走的地方不同，不能合并。"
companies:
  - meta
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开报告题型改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：Meta AI Coding：修复 maze solver，支持 keys、doors 与方向格"
    url: "https://www.1point3acres.com/interview/problems/company/meta/ai-coding-maze-solver"
    type: secondary
---

## 题目描述

来源：一亩三分地公开题型页列出 maze solver 的 debugging 与功能迭代。下面固定字符含义与返回格式，集中练习带状态的 BFS。

### 输入、接口与规则

实现 `maze_distance(grid) -> int`。输入是非空、等宽的字符串数组，最多 30×30。恰有一个 S 和一个 E；`.` 可走，`#` 是墙，`a/b/c` 是可重复拾取的 keys，`A/B/C` 是对应 doors。没有 key 时不能进入对应 door。`^v<>` 是方向格：离开该格时只能沿箭头方向，进入方向不限；其他格允许上下左右移动。每步 cost=1，不能越界。

返回从 S 到 E 的最少步数；无法到达时返回 -1。Keys 一旦拿到持续有效，不消耗；同一位置拿到新 key 后允许再次访问。不要求输出路径，不修改 grid。输入保证只使用上述字符；应在 enqueue 时记录 visited，避免循环与重复扩展。

### 输入输出示例

```text
grid=["S.AE", ".a##"] -> 返回 5。
路径可先走到 a，再经上方的 .、A 到 E。
grid=["S<E"] -> -1，因为中间的 < 不能向右离开。
```

## 回答思路

> **Situation / Task：** Maze 位置相同，持有的 keys 可能不同；目标是最少移动步数。  
> **Approach / Why：** BFS state 使用 (row, column, key_mask)，方向格限制 outgoing moves。  
> **Result / Check：** 测试拿 key 后重访、没有 key 的 door、方向限制和不可达。

## 解题思路与参考答案

我会先把 visited 从坐标改成坐标加 key mask。比如第一次经过门口没有 key，之后拿到 key 再回来，这两个状态能够继续走的地方不同，不能合并。

BFS 仍然适用，因为每次移动都花一步。先根据当前格决定能朝哪些方向走，再检查目标格的墙和 door；进入 key 格后更新 mask，最后把完整的新状态加入 visited。

### 完整参考实现

```python
from collections import deque


def maze_distance(grid):
    h, w = len(grid), len(grid[0])
    start = next((r, c) for r in range(h) for c in range(w) if grid[r][c] == 'S')
    queue = deque([(start[0], start[1], 0, 0)])
    seen = {(start[0], start[1], 0)}
    directions = {'^': [(-1, 0)], 'v': [(1, 0)], '<': [(0, -1)], '>': [(0, 1)]}
    while queue:
        r, c, mask, dist = queue.popleft()
        if grid[r][c] == 'E':
            return dist
        for dr, dc in directions.get(grid[r][c], [(-1, 0), (1, 0), (0, -1), (0, 1)]):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < h and 0 <= nc < w):
                continue
            char = grid[nr][nc]
            if char == '#':
                continue
            if char in 'ABC' and not (mask & (1 << (ord(char) - ord('A')))):
                continue
            newmask = mask | (1 << (ord(char) - ord('a'))) if char in 'abc' else mask
            state = (nr, nc, newmask)
            if state not in seen:
                seen.add(state)
                queue.append((*state, dist + 1))
    return -1
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert maze_distance(['S.AE', '.a##']) == 5
assert maze_distance(['S<E']) == -1
assert maze_distance(['SAE']) == -1
assert maze_distance(['SaAE']) == 3
assert maze_distance(['S.E']) == 2
assert maze_distance(['S#E', '...']) == 4
print('maze tests passed')
```

## 复杂度与追问

设格子数为 G、key 类型数 K=3，时间和空间均为 `O(G*2^K)`。追问若边有不同 cost，应使用 Dijkstra；若新增 bombs，还必须把持续发生的地图变化纳入 state。
