---
id: drustz-4fe2d75d9ce69c121e
section: forum-notes
order: 25
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 1: Basics'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 1: Basics'
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
## Level 1: Basics

### Requirement

Create a system to add new tasks, update them, and view their details.

### Operations

#### `addTask(timestamp, name, priority)` → `String`

- Creates a new task.
- Returns a unique ID like `"task_id_1"`, `"task_id_2"`, etc.
- IDs are created in order (1, 2, 3...).
- You can have multiple tasks with the same name. They will have different IDs.
- Ignore the `timestamp` for the logic in Level 1.

#### `updateTask(timestamp, taskId, name, priority)` → `boolean`

- Changes the name and priority of a specific task.
- Returns `true` if successful.
- Returns `false` if the `taskId` is not found.

#### `getTask(timestamp, taskId)` → `Optional<String>`

- Returns a string with task details in **JSON format**.
- Returns `Optional.empty()` if the task is not found.
- **Format Rules:**

Do not put spaces between keys and values.
- Keep spaces that are inside the name string.
- Order: first `name`, then `priority`.

### Level 1 Examples

| Queries | Explanations |
| --- | --- |
| `addTask(1, "Task 1", 5)` | Returns `"task_id_1"` |
| `addTask(2, "Task 1", 5)` | Returns `"task_id_2"`. Same name allowed. |
| `updateTask(3, "task_id_1", "Updated Task 1", 4)` | Returns `true`. Updates the first task. |
| `getTask(4, "task_id_1")` | Returns `'{"name":"Updated Task 1","priority":4}'`. No extra spaces. |
| `getTask(5, "task_id_3")` | Returns `Optional.empty()`. Task does not exist. |
| `updateTask(6, "task_id_3", "Non-existing Task", 1)` | Returns `false`. Task does not exist. |

### Level 1 Code

```python
from typing import Optional


class Task:
    def __init__(self, task_id: str, name: str, priority: int):
        self.task_id = task_id
        self.name = name
        self.priority = priority


class TaskManagementSystem:
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.task_counter = 0

    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        self.task_counter += 1
        task_id = f"task_id_{self.task_counter}"
        self.tasks[task_id] = Task(task_id, name, priority)
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
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
