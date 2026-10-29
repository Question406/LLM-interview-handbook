---
id: drustz-f4e50aea39229d43f3
section: forum-notes
order: 29
level: A
title: Anthropic 面试题库 · 一亩三分地会员版（完整） · Full Solution Code
quick: 作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Full Solution Code
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
## Full Solution Code

Here is the complete code with all features combined:

```python
from typing import Optional
from dataclasses import dataclass


@dataclass
class Assignment:
    task_id: str
    user_id: str
    start_time: int
    finish_time: int
    completed: bool = False


class Task:
    def __init__(self, task_id: str, name: str, priority: int):
        self.task_id = task_id
        self.name = name
        self.priority = priority


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

    # Level 1
    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        self.task_counter += 1
        task_id = f"task_id_{self.task_counter}"
        self.tasks[task_id] = Task(task_id, name, priority)
        self.creation_order[task_id] = self.task_counter
        return task_id

    def update_task(
        self, timestamp: int, task_id: str, name: str, priority: int
    ) -> bool:
        if task_id not in self.tasks:
            return False
        self.tasks[task_id].name = name
        self.tasks[task_id].priority = priority
        return True

    def get_task(self, timestamp: int, task_id: str) -> Optional[str]:
        if task_id not in self.tasks:
            return None
        task = self.tasks[task_id]
        return f'{{"name":"{task.name}","priority":{task.priority}}}'

    # Level 2
    def search_tasks(
        self, timestamp: int, name_filter: str, max_results: int
    ) -> list[str]:
        if max_results <= 0:
            return []

        matching = [
            task_id for task_id, task in self.tasks.items() if name_filter in task.name
        ]

        matching.sort(
            key=lambda tid: (-self.tasks[tid].priority, self.creation_order[tid])
        )
        return matching[:max_results]

    def list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]:
        if limit <= 0:
            return []

        task_ids = list(self.tasks.keys())
        task_ids.sort(
            key=lambda tid: (-self.tasks[tid].priority, self.creation_order[tid])
        )
        return task_ids[:limit]

    # Level 3
    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, quota)
        return True

    def _get_active_assignment_count(self, user: User, timestamp: int) -> int:
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
        active_count = self._get_active_assignment_count(user, timestamp)
        if active_count >= user.quota:
            return False

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

        active.sort(key=lambda a: (a.finish_time, a.start_time))
        return [a.task_id for a in active]

    # Level 4
    def complete_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        if task_id not in self.tasks or user_id not in self.users:
            return False

        user = self.users[user_id]
        active_assignments = [
            a
            for a in user.assignments
            if a.task_id == task_id
            and a.start_time <= timestamp < a.finish_time
            and not a.completed
        ]

        if not active_assignments:
            return False

        active_assignments.sort(key=lambda a: a.start_time)
        active_assignments[0].completed = True
        return True

    def get_overdue_assignments(self, timestamp: int, user_id: str) -> list[str]:
        if user_id not in self.users:
            return []

        user = self.users[user_id]
        overdue = [
            a
            for a in user.assignments
            if a.finish_time <= timestamp and not a.completed
        ]

        overdue.sort(key=lambda a: (a.finish_time, a.start_time))
        return [a.task_id for a in overdue]
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
