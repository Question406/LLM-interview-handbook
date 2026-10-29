---
id: drustz-797dfd45d764dba0ca
section: forum-notes
order: 238
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 3: Recovery and Immunity'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 3: Recovery and Immunity'
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## Part 3: Recovery and Immunity

### The Task

Now, let's add recovery. If a person has been infected for **D days**, they become **immune**.

Once a cell is immune:

- It cannot spread the virus anymore.
- It cannot get sick again.
Eventually, the grid will stop changing. Everyone will be either healthy or immune, and no active infections will be left.

**Question:** How many days until the infection stops completely?

### Things to Watch Out For

- **3 States:** A person can be Healthy, Infected (with an age), or Immune.
- **Timing:**

Healthy -> Infected (if a neighbor is sick).
- Infected -> Immune (after D days).
- **When to stop:** Stop when there are no more active infections.
- **Dying Waves:** The infection wave might die out because people recover and stop spreading it.

### Solution Details

We need to track exactly when each person got sick. We simulate one day at a time.

```python
def time_to_stable_state(grid: List[List[int]], D: int) -> int:
    """
    Grid values:
    - 0: Healthy
    - 1: Initially infected (day 0)

    D: Days until infected becomes immune

    Returns: Days until stable (no active infections)
    """
    if not grid or not grid[0]:
        return 0

    n, m = len(grid), len(grid[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # State tracking: -1 = immune, 0 = healthy, 1+ = infected on day X
    # Store infection day for each cell (-1 = immune, None = healthy)
    infection_day = [[None] * m for _ in range(n)]

    # Initialize: find initially sick cells (infected on day 0)
    active_infections = set()
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1:
                infection_day[i][j] = 0
                active_infections.add((i, j))

    if not active_infections:
        return 0  # No infections, already stable

    current_day = 0

    while active_infections:
        current_day += 1
        new_infections = set()
        new_immune = set()

        # Check who becomes immune today
        for i, j in active_infections:
            if infection_day[i][j] is not None and infection_day[i][j] >= 0:
                days_infected = current_day - infection_day[i][j]
                if days_infected >= D:
                    new_immune.add((i, j))

        # Remove newly immune cells from active list
        for i, j in new_immune:
            infection_day[i][j] = -1  # Mark as immune
            active_infections.discard((i, j))

        # Spread infection from remaining active cells
        for i, j in list(active_infections):
            for dr, dc in directions:
                ni, nj = i + dr, j + dc
                if 0 <= ni < n and 0 <= nj < m:
                    if infection_day[ni][nj] is None:  # Healthy
                        infection_day[ni][nj] = current_day
                        new_infections.add((ni, nj))

        active_infections.update(new_infections)

    return current_day
```



### Time and Space Complexity

- **Time Complexity:** O(days × n × m). The "days" part depends on `D` and how big the grid is.
- **Space Complexity:** O(n × m) to track the state of every cell.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
