---
id: drustz-30333a0ee54ed0e6ac
section: forum-notes
order: 237
level: A
title: 'OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Adding Immune Cells'
quick: '作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Part 2: Adding Immune Cells'
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
## Part 2: Adding Immune Cells

### The Task

Now, let's make it harder. Some cells are **immune**. This could mean they are vaccinated.

- **Immune cells cannot get sick.** They stay immune forever.
- **They do not spread the virus.** They act like walls.
- They have a special value, like `-1` or `2`.
How does this change the code?

### Things to Watch Out For

- **Blockers:** Immune cells are like walls. The BFS must go around them.
- **Reachability:** Some healthy people might be "safe" because they are surrounded by immune walls.
- **Stopping:**

If all *reachable* healthy people are sick, return the time.
- If any healthy person is safe behind a wall, return `-1`.

### Solution Approach

We can use the same BFS logic, but we make two changes:

- Ignore immune cells when looking for neighbors.
- Only count healthy (non-immune) cells when checking if we are done.

```python
def time_to_full_infection_with_immunity(grid: List[List[int]]) -> int:
    """
    Grid values:
    - 0: Healthy
    - 1: Infected
    - 2: Immune (cannot be infected, does not spread)
    """
    if not grid or not grid[0]:
        return -1

    n, m = len(grid), len(grid[0])
    queue = deque()
    infected_count = 0
    healthy_count = 0

    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1:
                queue.append((i, j, 0))
                infected_count += 1
            elif grid[i][j] == 0:
                healthy_count += 1
            # We ignore Immune cells (value 2)

    if healthy_count == 0:
        return 0  # All non-immune cells are already sick
    if infected_count == 0:
        return -1  # No infection source

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    max_time = 0

    while queue:
        row, col, time = queue.popleft()

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc

            if 0 <= new_row < n and 0 <= new_col < m and grid[new_row][new_col] == 0:
                grid[new_row][new_col] = 1
                healthy_count -= 1
                max_time = max(max_time, time + 1)
                queue.append((new_row, new_col, time + 1))

    return max_time if healthy_count == 0 else -1
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
