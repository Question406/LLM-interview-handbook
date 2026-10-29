---
id: p3a-openai-maximum-score-grid-path-limited-jumps
section: openai
order: 622
level: A
title: OpenAI：有限跨行跳跃的最大分数路径
quick: >-
  DP
  用当前行、列、已用跳数记录状态，按行递增转移。新分数更高就覆盖分数、条数和前驱，同分才累加路径数，最后从前驱还原一条最优路径；奖励依赖历史时还要扩状态。
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · OpenAI · maximum-score-grid-path-limited-jumps
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/maximum-score-grid-path-limited-jumps
    type: secondary
---

## 题目描述

给定有正负得分的网格、第一行起始列和最多跳跃次数，选择一条到达最后一行的路径。返回最高总分、达到该分数的路径数量以及任意一条最优路径。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `grid_path(grid, start, k, bonus=0)`：`grid` 是 R × C 的整数矩阵，可以有负数；从 `(0, start)` 出发，走到最后一行结束。
- 每步下移 1 行或 2 行，列变化为 -1、0 或 +1，不能出界。下移 2 行算一次 jump，最多 `k` 次，不必用完；被跳过的行不计分。
- 分数是经过的所有格子（包括起点）的值之和。如果某一步下移 1 行且列不变，额外加 `bonus`。
- 返回 `(best_score, count, path)`：最高分、达到最高分的路径条数（对 $10^9 + 7$ 取模）、一条最优路径的坐标列表。
- 假定网格非空且为矩形，start 与 k 合法。$R, C \le 50$，$K \le 10$。

### 示例

```text
grid_path([[1], [2], [3]], 0, 1)     -> (6, 1, [(0, 0), (1, 0), (2, 0)])
grid_path([[1], [-100], [3]], 0, 1)  -> (4, 1, [(0, 0), (2, 0)])
grid_path([[0, 0], [0, 0]], 0, 0)    -> (0, 2, [(0,0),(1,0)])  # 也允许返回经 (1,1) 的路径
grid_path([[1], [2]], 0, 0, bonus=5) -> (8, 1, [(0, 0), (1, 0)])
```

## 解题思路与参考答案

我会用当前行、当前列和已用跳数做 DP 状态，同时保存最高分、最优路径数和前驱。只用行和列不够，因为同一个格子，用掉 1 次跳跃和用掉 3 次跳跃到达，后面还能走的路不一样。

## 题目

给一个整数网格和第一行的起点，每步往下走，可以下移 1 行，也可以最多 K 次下移 2 行（跨过中间一行）。要求最高分数、一条最优路径、最优路径的条数，以及加上「奖励规则」之后的扩展版本。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理；`realInterview` 只表示网站把它收录为面经题型。下面的接口、约束和测试是手册补的练习约定。

所有移动都让行号变大，所以按行从上到下处理状态就是合法的拓扑序：处理一个状态时，能到达它的状态都已经算完了。

在同一套 DP 上同时求三个答案：

- 最高分：对每个状态取所有前驱转移过来的最大值；
- 一条最优路径：每个状态记下取到最大值的那个前驱，最后从终点倒推；
- 最优路径条数：只对达到同一最优分的前驱累加条数。分数更高的前驱出现时，条数要重置，不能把所有路径都数进去。

奖励扩展要看奖励依赖什么。如果奖励只依赖最后一步（比如这里的「下移 1 行且列不变」），当前状态就够用；如果依赖更早的历史，比如连续几步的方向，就必须把这段历史也放进状态，不能直接把奖励加到没有记忆的 DP 上。

动手前要和面试官确认：允许哪些移动方向，被跳过的行算不算分，跳跃次数没用完能不能结束。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `grid_path(grid, start, k, bonus=0)`：`grid` 是 R × C 的整数矩阵，可以有负数；从 `(0, start)` 出发，走到最后一行结束。
- 每步下移 1 行或 2 行，列变化为 -1、0 或 +1，不能出界。下移 2 行算一次 jump，最多 `k` 次，不必用完；被跳过的行不计分。
- 分数是经过的所有格子（包括起点）的值之和。如果某一步下移 1 行且列不变，额外加 `bonus`。
- 返回 `(best_score, count, path)`：最高分、达到最高分的路径条数（对 $10^9 + 7$ 取模）、一条最优路径的坐标列表。
- 网格为空、不是矩形、`start` 越界或 `k < 0` 时抛 `ValueError`。$R, C \le 50$，$K \le 10$。

### 输入输出示例

```text
grid_path([[1], [2], [3]], 0, 1)     -> (6, 1, [(0, 0), (1, 0), (2, 0)])
grid_path([[1], [-100], [3]], 0, 1)  -> (4, 1, [(0, 0), (2, 0)])
grid_path([[0, 0], [0, 0]], 0, 0)    -> (0, 2, ...)
grid_path([[1], [2]], 0, 0, bonus=5) -> (8, 1, [(0, 0), (1, 0)])
```

第二行用一次 jump 跳过了 -100；第三行有两条同分路径，分别走到 `(1, 0)` 和 `(1, 1)`。

### 解题思路与正确性

`best`、`count`、`parent` 三个字典都以 `(row, col, used)` 为键，只保存可达状态。按行、列、跳数的顺序遍历，每个状态最多向 6 个后继转移（2 种步长 × 3 种列变化）。

更新规则：新分数更高就覆盖分数、把条数设成前驱的条数、记录前驱；分数相同就累加条数。因为一个状态的所有前驱都在更早的行里，处理它时它的分数和条数已经是最终值，再往后传不会出错。

最后在最后一行、跳数不超过 K 的所有状态里取最高分，把达到最高分的状态的条数加起来。不同终点状态对应的路径必然不同（终点列不同或跳跃次数不同），所以直接相加不会重复计数。

### 完整参考实现（Python 3）

```python
MOD = 10**9 + 7


def grid_path(grid, start, k, bonus=0):
    """从 (0, start) 走到最后一行，每步下移 1 行或 2 行（下移 2 行算一次 jump，最多 k 次），
    列变化 -1/0/+1。分数是经过格子的值之和；下移 1 行且列不变时额外加 bonus。

    返回 (最高分, 最高分路径条数 mod 1e9+7, 一条最优路径的坐标列表)。
    """
    if not grid or not grid[0]:
        raise ValueError("grid must be non-empty")
    if any(len(row) != len(grid[0]) for row in grid):
        raise ValueError("grid must be rectangular")
    if k < 0:
        raise ValueError("k must be non-negative")
    if not 0 <= start < len(grid[0]):
        raise ValueError("start column out of range")

    rows, cols = len(grid), len(grid[0])
    # 状态 (row, col, jumps_used)；只记录可达状态
    origin = (0, start, 0)
    best = {origin: grid[0][start]}
    count = {origin: 1}
    parent = {}

    # 所有转移都让行号变大，按行从上到下处理就是拓扑序：处理某个状态时，它的所有前驱都已处理完
    for row in range(rows):
        for col in range(cols):
            for used in range(k + 1):
                state = (row, col, used)
                if state not in best:
                    continue
                for step in (1, 2):
                    next_row = row + step
                    next_used = used + (step == 2)
                    if next_row >= rows or next_used > k:
                        continue
                    for next_col in (col - 1, col, col + 1):
                        if not 0 <= next_col < cols:
                            continue
                        target = (next_row, next_col, next_used)
                        score = best[state] + grid[next_row][next_col]
                        if step == 1 and next_col == col:
                            score += bonus
                        if target not in best or score > best[target]:
                            best[target] = score
                            count[target] = count[state]
                            parent[target] = state
                        elif score == best[target]:
                            # 同分时累加路径数；只统计达到最优分的路径
                            count[target] = (count[target] + count[state]) % MOD

    finals = [state for state in best if state[0] == rows - 1]
    top_score = max(best[state] for state in finals)
    winners = [state for state in finals if best[state] == top_score]
    total = sum(count[state] for state in winners) % MOD

    path = []
    state = min(winners)
    while True:
        path.append(state[:2])
        if state not in parent:
            break
        state = parent[state]
    path.reverse()
    return top_score, total, path
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert grid_path([[1], [2], [3]], 0, 1) == (6, 1, [(0, 0), (1, 0), (2, 0)])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


# 单列，逐行走最好
assert grid_path([[1], [2], [3]], 0, 1) == (6, 1, [(0, 0), (1, 0), (2, 0)])
assert grid_path([[1], [2], [3]], 0, 0)[0] == 6

# 用一次 jump 跳过负分行，被跳过的行不计分
assert grid_path([[1], [-100], [3]], 0, 1) == (4, 1, [(0, 0), (2, 0)])

# 两条同分路径：(0,0)->(1,0) 和 (0,0)->(1,1)
assert grid_path([[0, 0], [0, 0]], 0, 0)[1] == 2

# 下移 1 行且列不变，加 bonus
assert grid_path([[1], [2]], 0, 0, 5)[0] == 8

# 只有一行时，起点就是终点
assert grid_path([[-3]], 0, 2) == (-3, 1, [(0, 0)])

# 非法输入
expect_value_error(grid_path, [[1, 2], [3]], 0, 0)
expect_value_error(grid_path, [[1]], 1, 0)
expect_value_error(grid_path, [[1]], 0, -1)
```

### 复杂度与追问

状态数是 O(RCK)，每个状态最多 6 个转移，所以时间是 O(RCK)；`best`、`count`、`parent` 一共占 O(RCK) 空间。

- 只要分数、不要路径时能省空间吗？可以。转移只看前两行，滚动保存最近两行的状态，空间降到 O(CK)。
- 奖励依赖更早的历史怎么办？把需要的历史放进状态。比如奖励「连续两步都直走」，就要在状态里加上「上一步是否直走」，状态数相应翻倍。本题的 `bonus` 只依赖最后一步，当前状态已经足够。
