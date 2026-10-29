---
id: drustz-6dd2f36128c4d4c0f6
section: forum-notes
order: 26
level: A
title: 'Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 2: Search & Sort'
quick: '作者文档章节 · Anthropic 面试题库 · 一亩三分地会员版（完整） · Level 2: Search & Sort'
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
## Level 2: Search & Sort

### Requirement

Add tools to find tasks and list them in a specific order.

### New Operations

#### `searchTasks(timestamp, nameFilter, maxResults)` → `List<String>`

- Finds tasks where the name contains the `nameFilter`.
- Returns a list of task IDs (up to `maxResults`).
- **Sorting Rules:**

First, by **priority** (High to Low).
- If priorities are equal, sort by **creation order** (Low IDs first).
- If `maxResults` is 0 or less, return an empty list.

#### `listTasksSorted(timestamp, limit)` → `List<String>`

- Lists all task IDs up to the `limit`.
- Uses the same sorting rules as search: **priority (High -> Low)**, then **creation order**.

### Level 2 Examples

| Queries | Explanations |
| --- | --- |
| `addTask(1, "Alpha", 10)` | Returns `"task_id_1"` |
| `addTask(2, "Bravo", 15)` | Returns `"task_id_2"` |
| `addTask(3, "Bravo Alpha", 5)` | Returns `"task_id_3"` |
| `listTasksSorted(4, 2)` | Returns `["task_id_2", "task_id_1"]`. Sorts by priority. |
| `searchTasks(5, "Bra", 5)` | Returns `["task_id_2", "task_id_3"]`. Matches "Bravo". |
| `updateTask(6, "task_id_1", "Alpha Updated", 20)` | Returns `true`. Priority is now 20. |
| `searchTasks(7, "Al", 1)` | Returns `["task_id_1"]`. "Alpha Updated" is now highest priority. |

### Level 2 Code

Add these methods to the previous code:

```python
class TaskManagementSystem:
    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.task_counter = 0
        self.creation_order: dict[str, int] = {}  # Maps task_id to creation number

    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        self.task_counter += 1
        task_id = f"task_id_{self.task_counter}"
        self.tasks[task_id] = Task(task_id, name, priority)
        self.creation_order[task_id] = self.task_counter
        return task_id

    # ... Include Level 1 methods here ...

    def search_tasks(
        self, timestamp: int, name_filter: str, max_results: int
    ) -> list[str]:
        if max_results <= 0:
            return []

        matching = [
            task_id for task_id, task in self.tasks.items() if name_filter in task.name
        ]

        # Sort: Priority Descending (-), then Creation Order Ascending (+)
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
```

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-anthropic.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-anthropic.md)。作者整理资料；许可和第三方来源范围见阅读指南。
