---
id: p3a-openai-infection-spread-cellular-automata
section: openai
order: 601
level: A
title: "OpenAI：感染传播：分阶段规则的网格模拟"
quick: "基础版用多源 BFS 按天扩展；有阈值和有限传染期时，记录感染日，每天先收集新感染、再统一写回。当天无新增就停，因为旧感染源只会减少；无法感染全部非墙格时返回 -1。"
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
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · infection-spread-cellular-automata"
    url: https://www.1point3acres.com/interview/problems/company/openai/infection-spread-cellular-automata
    type: secondary
---

## 题目描述

给定带初始感染者、可感染格子和墙的网格，按同步的逐日规则模拟感染传播。返回感染覆盖所有非墙格子的最早天数，以及每个格子的首次感染时间；若无法完全覆盖，天数返回 -1。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- 网格字符：`X` 是初始感染，`.` 是可感染的格子，`#` 是免疫的墙。
- `spread(grid, threshold=1, infectious_days=None) -> (days, infected_at)`：每天，一个未感染的 `.` 如果四邻居里至少有 `threshold` 个此刻有传染性的格子，第二天就被感染。
- 在第 d 天被感染的格子，传染期是 $[d, d + k)$，其中 k 是 `infectious_days`；`infectious_days=None` 表示永远有传染性。
- `days` 是全部非墙格子被感染所需的天数，做不到时为 -1。`infected_at` 是每个格子的感染日，墙和没被感染的格子是 `None`。
- `threshold` 在 1 到 4 之间，`infectious_days` 至少为 1，网格非空、各行等长、不超过 $100 \times 100$。

### 示例

```text
spread(["X.."], infectious_days=1)   -> (2, [[0, 1, 2]])
spread(["X#."])                      -> (-1, [[0, None, None]])
spread(["X.X"], threshold=2)         -> (1, [[0, 1, 0]])
spread(["XX", ".."], threshold=2)    -> (-1, [[0,0],[None,None]])
```

## 解题思路与参考答案

基础版用多源 BFS；加入阈值和有限传染期后，改为记录感染日并每天同步重算。基础版本只有一个感染邻居就会感染、且永久有传染性：所有初始感染格一起入队，按层扩展，层数就是天数。要注意更新是同步的，一天之内只有前一天结束时已经感染的格子能传播，当天新感染的格子要到第二天才开始传。

## 题目

在网格上模拟感染扩散：一些格子一开始就被感染，每过一天，感染会传给相邻的格子。题目分阶段加规则，比如免疫的格子、需要多个感染邻居才会被感染的阈值、感染后只在一段时间内有传染性，要求算出全部被感染需要几天，或者判断永远感染不完。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 在 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。网站列了五个小问，这份练习只固定其中一种分阶段变体；接口、约束和测试是手册补的练习约定，不是原题。

加上阈值或传染期之后，BFS「每个格子只访问一次」的前提就不成立了。一个格子今天邻居不够，明天可能就够了；一个感染源今天还有传染性，明天可能就失效了。这时要显式记录每个格子的感染时间，每天重新判断，而不是继续套 BFS。

自查时至少跑这几种情况：只有一个格子、被墙隔开的孤立区域、同一天新感染的格子不能当天继续传播，以及永远感染不完、应该返回 -1 的情况。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- 网格字符：`X` 是初始感染，`.` 是可感染的格子，`#` 是免疫的墙。
- `spread(grid, threshold=1, infectious_days=None) -> (days, infected_at)`：每天，一个未感染的 `.` 如果四邻居里至少有 `threshold` 个此刻有传染性的格子，第二天就被感染。
- 在第 d 天被感染的格子，传染期是 $[d, d + k)$，其中 k 是 `infectious_days`；`infectious_days=None` 表示永远有传染性。
- `days` 是全部非墙格子被感染所需的天数，做不到时为 -1。`infected_at` 是每个格子的感染日，墙和没被感染的格子是 `None`。
- `threshold` 在 1 到 4 之间，`infectious_days` 至少为 1，网格非空、各行等长、不超过 $100 \times 100$，否则抛 `ValueError`。

### 输入输出示例

```text
spread(["X.."], infectious_days=1)   -> (2, [[0, 1, 2]])
spread(["X#."])                      -> (-1, [[0, None, None]])
spread(["X.X"], threshold=2)         -> (1, [[0, 1, 0]])
spread(["XX", ".."], threshold=2)    -> (-1, ...)   # 下面两格各只有一个感染邻居
```

### 解题思路与正确性

每一天先扫描整个网格，把满足条件的格子放进 `newly_infected`，整天算完之后才写入感染时间。这样当天判断用的全是前一天结束时的状态，保证了同步更新。

判断「有传染性」只看感染时间：已感染，并且距感染日不到 `infectious_days` 天。

如果某一天没有任何新感染，就可以停下。原因是之后不会再有新的感染源，而已有的感染源只会因为过了传染期而减少，任何格子的感染邻居数都不会再增加，原来达不到阈值的以后也达不到。

### 完整参考实现（Python 3）

```python
CELLS = {"X", ".", "#"}  # 初始感染、可感染、免疫墙
DIRECTIONS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def validate(grid, threshold, infectious_days):
    if not grid or not grid[0]:
        raise ValueError("grid must be non-empty")
    width = len(grid[0])
    for row in grid:
        if len(row) != width:
            raise ValueError("grid rows must have the same length")
        if any(cell not in CELLS for cell in row):
            raise ValueError(f"grid cells must be one of {sorted(CELLS)}")
    if threshold not in range(1, 5):
        raise ValueError(f"threshold must be in 1..4, got {threshold}")
    if infectious_days is not None and infectious_days < 1:
        raise ValueError(f"infectious_days must be >= 1, got {infectious_days}")


def spread(grid, threshold=1, infectious_days=None):
    """同步模拟感染扩散，返回 (天数, 感染时间矩阵)。

    每天，一个未感染的 "." 格如果有至少 threshold 个四邻居此刻有传染性，第二天就被感染。
    一个格子在第 d 天被感染，传染期是 [d, d + infectious_days)；None 表示永远有传染性。
    天数是最后一次有新感染的那一天；仍有非墙格子没被感染时返回 -1。墙和未感染格的时间为 None。
    """
    validate(grid, threshold, infectious_days)
    height, width = len(grid), len(grid[0])
    infected_at = [[0 if cell == "X" else None for cell in row] for row in grid]

    def is_contagious(row, col, day):
        start = infected_at[row][col]
        if start is None:
            return False
        return infectious_days is None or day - start < infectious_days

    def contagious_neighbors(row, col, day):
        count = 0
        for d_row, d_col in DIRECTIONS:
            r, c = row + d_row, col + d_col
            if 0 <= r < height and 0 <= c < width and is_contagious(r, c, day):
                count += 1
        return count

    day = 0
    while True:
        # 先算出当天所有新感染，整天算完再写入，保证同一天内的更新是同步的
        newly_infected = []
        for row in range(height):
            for col in range(width):
                if grid[row][col] != "." or infected_at[row][col] is not None:
                    continue
                if contagious_neighbors(row, col, day) >= threshold:
                    newly_infected.append((row, col))
        # 没有新感染时，有传染性的格子只会越来越少，以后也不会再有新感染
        if not newly_infected:
            break
        day += 1
        for row, col in newly_infected:
            infected_at[row][col] = day

    unreachable = any(
        grid[row][col] != "#" and infected_at[row][col] is None
        for row in range(height)
        for col in range(width)
    )
    return (-1 if unreachable else day), infected_at
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert spread(["X.."], infectious_days=1) == (2, [[0, 1, 2]])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 传染期 1 天：每个格子只在被感染当天传给下一格
assert spread(["X.."], infectious_days=1) == (2, [[0, 1, 2]])

# 墙挡住传播
assert spread(["X#."])[0] == -1

# 阈值 2：下面两格各只有一个感染邻居，永远达不到阈值
assert spread(["XX", ".."], threshold=2)[0] == -1

# 阈值 2 能传开的情况：中间格同时挨着两个感染源
assert spread(["X.X"], threshold=2) == (1, [[0, 1, 0]])

# 左下角要等到第 1 天才凑齐两个邻居；永久传染时能感染，
# 传染期只有 1 天时左上角那个源已经失效，左下角永远凑不齐
assert spread(["XX.", "..X"], threshold=2) == (2, [[0, 0, 1], [2, 1, 0]])
assert spread(["XX.", "..X"], threshold=2, infectious_days=1)[0] == -1

# 全是墙：不需要任何一天
assert spread(["##"]) == (0, [[None, None]])

expect_value_error(spread, [])                      # 空网格
expect_value_error(spread, ["X.", "."])             # 行长不一致
expect_value_error(spread, ["X?"])                  # 非法字符
expect_value_error(spread, ["X."], threshold=5)     # 阈值超出 1..4
expect_value_error(spread, ["X."], infectious_days=0)
```

### 复杂度与追问

设网格有 H 行 W 列。每天扫描一遍是 O(HW)，最多持续 O(HW) 天，最坏 $O((HW)^2)$ 时间，空间 O(HW)。

- 追问「能不能更快」：`threshold=1` 且永久传染时，直接用多源 BFS，O(HW)。
- 追问「有阈值和传染期时怎么优化」：给每个格子维护「当前有传染性的邻居数」。某个格子被感染时给它的邻居计数加一，过了传染期时再减一，按天把这些变化放进事件队列。只有计数发生变化的格子才需要重新检查是否达到阈值，不用每天扫全图。
