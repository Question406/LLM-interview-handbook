---
id: openai-grid-visit-targets-mask
section: openai
order: 929
level: A
title: "OpenAI：Grid 上访问全部 target cells 的最少步数"
quick: "我会给每个 target 分配一个 bit，走进 target 格时把对应 bit 置一。位置和 mask 一起才能描述接下来还要完成什么。"
companies:
  - openai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开报告题型改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：OpenAI：Grid 上访问全部 target cells 的最少步数"
    url: "https://aceoffer.app/interviews/oai_shortest_path_to_visit_all_points_on_a_grid"
    type: secondary
---

## 题目描述

来源：AceOffer 公开题型标题为 shortest path to visit all points on a grid。下面明确 obstacles、固定起点与任意终点，作为完整的 BFS + bitmask 练习。

### 输入、接口与规则

实现 `visit_targets(grid, start, targets) -> int`。输入为非空等宽 grid，`.` 可走，`#` 是 obstacle；只允许上下左右移动，每步 cost=1。start 为可走格 (row,column)，targets 为最多 8 个互不相同的可走格，可能包含 start。Grid 最多 20×20；输入保证坐标有效，不修改输入。

从 start 出发，访问全部 targets 至少一次后可停在任意格。返回所需最少步数；存在无法访问的 target 返回 -1。可以重复经过格子，targets 为空返回 0。不要求输出路径，也不要求回到 start。请解释为什么只按坐标记录 visited 会漏掉正确答案。

### 输入输出示例

```text
grid=["...",".#.","..."]，start=(0,0)，targets=[(0,2),(2,2)] -> 4。
grid=[".#."]，start=(0,0)，targets=[(0,2)] -> -1。
任意合法 grid，targets=[] -> 0。
```

## 回答思路

> **Situation / Task：** 到过同一格但完成的 targets 不同，应视为不同状态。  
> **Approach / Why：** BFS state=(r,c,visited_target_mask)，首次 mask 全满即得到最优答案。  
> **Result / Check：** 检查起点也是 target、不可达、空 targets 与需要重访的路径。

## 解题思路与参考答案

我会给每个 target 分配一个 bit，走进 target 格时把对应 bit 置一。位置和 mask 一起才能描述接下来还要完成什么。

每步 cost 相同，所以用 BFS；第一次遇到 full mask 的 state 就可以返回。只有坐标相同还不能去重，否则可能把“已经访问左边目标再回来”的有效路线删掉。

### 完整参考实现

```python
from collections import deque


def visit_targets(grid, start, targets):
    bits = {pos: 1 << i for i, pos in enumerate(targets)}
    full = (1 << len(targets)) - 1
    initial = bits.get(start, 0)
    queue = deque([(*start, initial, 0)])
    seen = {(*start, initial)}
    while queue:
        r, c, mask, steps = queue.popleft()
        if mask == full:
            return steps
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] != '#':
                state = (nr, nc, mask | bits.get((nr, nc), 0))
                if state not in seen:
                    seen.add(state)
                    queue.append((*state, steps + 1))
    return -1
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert visit_targets(['...', '.#.', '...'], (0, 0), [(0, 2), (2, 2)]) == 4
assert visit_targets(['.#.'], (0, 0), [(0, 2)]) == -1
assert visit_targets(['.'], (0, 0), []) == 0
assert visit_targets(['.'], (0, 0), [(0, 0)]) == 0
assert visit_targets(['.....'], (0, 2), [(0, 0), (0, 4)]) == 6
# On an obstacle-free grid, brute-force all target visit orders using Manhattan distance.
from itertools import permutations, combinations

points = [(0, 0), (0, 2), (2, 0), (2, 2)]
for targets in combinations(points, 3):
    expected = min(
        sum(
            abs(a[0] - b[0]) + abs(a[1] - b[1])
            for a, b in zip(((1, 1),) + order, order)
        )
        for order in permutations(targets)
    )
    assert visit_targets(['...'] * 3, (1, 1), targets) == expected
print('grid targets tests passed')
```

## 复杂度与追问

格子数 G、target 数 K，时间和空间均为 `O(G*2^K)`。若 grid 很大而 targets 少，可先 BFS 求关键点间距离，再用 subset DP；先确认所有关键点可达。
