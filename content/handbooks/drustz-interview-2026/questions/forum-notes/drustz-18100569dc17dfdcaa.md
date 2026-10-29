---
id: drustz-18100569dc17dfdcaa
section: forum-notes
order: 198
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Reference Solution
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Reference Solution
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
## Reference Solution

```python
from typing import List, Optional, Tuple

Assignment = Tuple[int, int, int]


def build_basic_schedule(t: int, m: int, h: int, k: int) -> Optional[List[Assignment]]:
    """
    Part 1: ignore prefix balance and build any valid schedule.
    """
    if k == 0:
        return []
    if t <= 0 or m <= 0 or h <= 0:
        return None
    if k > t:
        return None

    schedule: List[Assignment] = []
    for human in range(h):
        for offset in range(k):
            task = (human + offset) % t
            model = 0
            schedule.append((task, model, human))
    return schedule


def build_balanced_schedule(
    t: int, m: int, h: int, k: int
) -> Optional[List[Assignment]]:
    """
    Part 2: build a schedule such that:
      - each human appears at least k times
      - each (task, human) pair appears at most once
      - for every task, model counts stay prefix-balanced
      - task-human balance is automatic because counts are only 0/1

    Returns a minimal-length valid schedule of exactly h * k assignments,
    or None if impossible.
    """
    if k == 0:
        return []
    if t <= 0 or m <= 0 or h <= 0:
        return None
    if k > t:
        return None

    schedule: List[Assignment] = []
    task_seen = [0] * t

    for round_idx in range(k):
        for human in range(h):
            task = (human + round_idx) % t
            model = task_seen[task] % m
            schedule.append((task, model, human))
            task_seen[task] += 1

    return schedule
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。
