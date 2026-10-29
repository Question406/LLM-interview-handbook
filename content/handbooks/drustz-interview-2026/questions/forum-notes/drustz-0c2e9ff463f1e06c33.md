---
id: drustz-0c2e9ff463f1e06c33
section: forum-notes
order: 27
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 3: Users & Assignments'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 3: Users & Assignments'
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md
    type: primary
---
## Level 3: Users & Assignments

### Requirement

Add users to the system. Users have a limit on how many tasks they can do at once (quota). Tasks are assigned for a specific time period.

### New Operations

#### `addUser(timestamp, userId, quota)` → `boolean`

- Adds a user with a specific task limit (`quota`).
- Returns `true` if successful.
- Returns `false` if the user ID already exists.

#### `assignTask(timestamp, taskId, userId, finishTime)` → `boolean`

- Assigns a task to a user from `timestamp` until `finishTime`.
- **Quota Rule:** Each active task uses 1 quota slot.
- Returns `false` if:

Task or User doesn't exist.
- User has reached their quota limit at this moment.
- When `timestamp` reaches `finishTime`, the task expires and the quota slot is freed automatically.
- You can assign the same task multiple times. Each assignment is separate.

#### `getUserTasks(timestamp, userId)` → `List<String>`

- Gets a list of IDs for tasks currently assigned to the user.
- A task is "active" if: `start_time <= timestamp < finish_time`.
- **Sorting:** Sort by `finish_time` (soonest first). Tie-break with assignment time.

### Level 3 Examples

| Queries | Explanations |
| --- | --- |
| `addUser(1, "user1", 2)` | Returns `true`. Quota is 2. |
| `addUser(2, "user1", 3)` | Returns `false`. User exists. |
| `addTask(3, "Task A", 10)` | Returns `"task_id_1"` |
| `addTask(4, "Task B", 5)` | Returns `"task_id_2"` |
| `assignTask(5, "task_id_1", "user1", 15)` | Returns `true`. Assigned until time 15. |
| `getUserTasks(6, "user1")` | Returns `["task_id_1"]` |
| `assignTask(7, "task_id_2", "user1", 20)` | Returns `true`. Assigned until time 20. |
| `getUserTasks(8, "user1")` | Returns `["task_id_1", "task_id_2"]`. |
| `assignTask(9, "task_id_1", "user1", 25)` | Returns `false`. Quota full (2 active tasks). |
| `getUserTasks(16, "user1")` | Returns `["task_id_2"]`. Task 1 expired at 15. |
| `getUserTasks(21, "user1")` | Returns `[]`. Both tasks expired. |

### Level 3 Code

```python
from dataclasses import dataclass


@dataclass
class Assignment:
    task_id: str
    user_id: str
    start_time: int
    finish_time: int
    completed: bool = False


class User:
    def __init__(self, user_id: str, quota: int):
        self.user_id = user_id
        self.quota = quota
        self.assignments: list[Assignment] = []


class TaskManagementSystem:
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.task_counter = 0
        self.creation_order: dict[str, int] = {}
        self.users: dict[str, User] = {}

    # ... Include Level 1 & 2 methods here ...

    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, quota)
        return True

    def _get_active_assignment_count(self, user: User, timestamp: int) -> int:
        """Count how many assignments are active right now."""
        return sum(
            1
            for a in user.assignments
            if a.start_time <= timestamp < a.finish_time and not a.completed
        )

    def assign_task(
        self, timestamp: int, task_id: str, user_id: str, finish_time: int
    ) -> bool:
        if task_id not in self.tasks or user_id not in self.users:
            return False

        user = self.users[user_id]

        # Check if user has space in their quota
        active_count = self._get_active_assignment_count(user, timestamp)
        if active_count >= user.quota:
            return False

        # Add new assignment
        assignment = Assignment(task_id, user_id, timestamp, finish_time)
        user.assignments.append(assignment)
        return True

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
        if user_id not in self.users:
            return []

        user = self.users[user_id]
        active = [
            a
            for a in user.assignments
            if a.start_time <= timestamp < a.finish_time and not a.completed
        ]

        # Sort by finish_time, then start_time
        active.sort(key=lambda a: (a.finish_time, a.start_time))

        return [a.task_id for a in active]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
