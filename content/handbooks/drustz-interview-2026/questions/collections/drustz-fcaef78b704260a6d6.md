---
id: drustz-fcaef78b704260a6d6
section: collections
order: 33
level: A
title: hack2hire 完整题解（抓取的解锁内容） · Design a Task Assignment System
quick: 作者文档章节 · hack2hire 完整题解（抓取的解锁内容） · Design a Task Assignment System
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 主题题库与复习资料
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/hack2hire-premium.md
    type: primary
---
## Design a Task Assignment System

### Part 1
Design a task tracking system that stores tasks by unique IDs, supports updating task metadata, and retrieves task details on demand.

Implement the `TaskManager` class:
- `TaskManager()` Initializes the task manager with an empty task store.

- `String addTask(int timestamp, String name, int priority)` Adds a new task with the given `name` and `priority`. Returns the unique ID assigned to this task in the format `"taskId<n>"`, where `n` is a sequential counter starting from `1`. Tasks with **identical** names and priorities are allowed; each receives its own unique ID.

- `boolean updateTask(int timestamp, String taskId, String name, int priority)` Updates the `name` and `priority` of the task identified by `taskId`. Returns `true` if the task exists and was updated, or `false` if `taskId` is not found.

**概要**:
- Design a class to manage tasks with sequential unique IDs.
- Implement methods to add, update, and retrieve task details.
- Use a hash map for efficient storage and lookup by ID.

**考察点**:
- Hash map implementation for key-value storage.
- Class state management and instance variables.
- Sequential identifier generation.
- Handling missing keys and edge cases.

**常用模式**:
- Hashing
- Design

**提示**:
- Consider which data structure allows for fast retrieval when you only know the unique task ID.
- You'll need a separate integer variable to track the next ID number to assign.
- Store the task details (name, priority) in a simple object or tuple mapped to the ID string within your collection.

**可能的 follow-up**:
- How would you modify the system to support searching tasks by name or priority efficiently?
- If the number of tasks grows to millions, how would you optimize memory usage or persistence?
- How would you ensure thread-safety if multiple threads call these methods simultaneously?
- What changes would be needed to delete tasks or implement soft deletes?

### Part 2
Design a task tracking system that stores tasks by unique IDs, supports updating task metadata, and retrieves task details on demand.

Implement the `TaskManager` class:
- `TaskManager()` Initializes the task manager with an empty task store.

- `String addTask(int timestamp, String name, int priority)` Adds a new task with the given `name` and `priority`. Returns the unique ID assigned to this task in the format `"taskId<n>"`, where `n` is a sequential counter starting from `1`. Tasks with **identical** names and priorities are allowed; each receives its own unique ID.

- `boolean updateTask(int timestamp, String taskId, String name, int priority)` Updates the `name` and `priority` of the task identified by `taskId`. Returns `true` if the task exists and was updated, or `false` if `taskId` is not found.

**概要**:
- Design a TaskManager class supporting add, update, search, and sorted listing of tasks.
- Tasks must be sorted by priority descending and creation order ascending, with creation order resolved via numeric ID comparison.
- Search functionality requires case-sensitive substring matching and result limiting.

**考察点**:
- Hash Map usage for efficient task storage and O(1) lookups.
- Custom comparator implementation for multi-criteria sorting.
- String substring search and filtering logic.
- Distinction between numeric ordering and lexicographic string ordering.

**常用模式**:
- Hashing
- Sorting
- Design

**提示**:
- Ensure the sort comparator treats the task ID's creation order as a numeric value to correctly order 'taskId1' before 'taskId10'.
- Use a hash map for direct task access, but recognize that `searchTasks` and `listTasksSorted` will likely require iterating through all entries.
- Handle edge cases explicitly: return empty lists for non-positive limits and treat an empty `nameFilter` as a wildcard matching all tasks.

**可能的 follow-up**:
- How would you optimize `searchTasks` performance if the dataset grows to millions of tasks?
- Can you maintain the tasks in a pre-sorted structure to accelerate `listTasksSorted` without re-sorting?
- How would you extend this design to support concurrent modifications safely?

### Part 3
Design a task tracking system that stores tasks by unique IDs, supports updating task metadata, and retrieves task details on demand.

Implement the `TaskManager` class:
- `TaskManager()` Initializes the task manager with an empty task store.

- `String addTask(int timestamp, String name, int priority)` Adds a new task with the given `name` and `priority`. Returns the unique ID assigned to this task in the format `"taskId<n>"`, where `n` is a sequential counter starting from `1`. Tasks with **identical** names and priorities are allowed; each receives its own unique ID.

- `boolean updateTask(int timestamp, String taskId, String name, int priority)` Updates the `name` and `priority` of the task identified by `taskId`. Returns `true` if the task exists and was updated, or `false` if `taskId` is not found.

**概要**:
- Implement user management with constraints on simultaneous active tasks.
- Validate task assignments by detecting interval overlaps and verifying dynamic quota limits.
- Query active tasks for a user within specific time windows.

**考察点**:
- Sweep-line algorithms for interval analysis and peak load detection.
- Hash table design for O(1) user and task lookups.
- Interval clipping and overlap logic.
- Event sorting and tie-breaking rules for half-open intervals.
- State simulation over time ranges.

**常用模式**:
- Sweep-line
- Hashing
- Sorting
- Interval Operations

**提示**:
- To verify the quota, you only need to check the count of active tasks at critical moments defined by interval boundaries, not every integer time point.
- Clip existing assignments to the new request's window and generate events marking where the load increases or decreases.
- Sort these events by time; ensure you process end-of-interval events before start-of-interval events at the same timestamp to correctly handle half-open boundaries during the sweep.

**可能的 follow-up**:
- How would you optimize `assignTask` if a user maintains thousands of assignments?
- Could you replace the linear scan with an Interval Tree or Segment Tree to speed up conflict detection?
- How would you extend this system to support concurrency and thread-safe updates?
- What changes if the timestamp values are extremely large or sparse?

### Part 4
Design a task tracking system that stores tasks by unique IDs, supports updating task metadata, and retrieves task details on demand.

Implement the `TaskManager` class:
- `TaskManager()` Initializes the task manager with an empty task store.

- `String addTask(int timestamp, String name, int priority)` Adds a new task with the given `name` and `priority`. Returns the unique ID assigned to this task in the format `"taskId<n>"`, where `n` is a sequential counter starting from `1`. Tasks with **identical** names and priorities are allowed; each receives its own unique ID.

- `boolean updateTask(int timestamp, String taskId, String name, int priority)` Updates the `name` and `priority` of the task identified by `taskId`. Returns `true` if the task exists and was updated, or `false` if `taskId` is not found.

**概要**:
- Implement task completion logic that frees user quotas upon success.
- Track and retrieve overdue assignments based on expiration and completion status.
- Manage complex state transitions for task instances over time.

**考察点**:
- State management and entity lifecycle tracking.
- Interval logic and time-based filtering.
- Efficient lookup using hash maps.
- Resource quota management logic.

**常用模式**:
- Hashing
- Sorting
- Design

**提示**:
- Consider storing assignments in a map keyed by task ID within each user's record to enable direct access rather than scanning all assignments.
- Track completion by recording a `completedAt` timestamp on the assignment object, which effectively shortens its active interval without deleting the record.
- When checking for overdue items, verify that the assignment's `finishTime` is less than or equal to the query timestamp while ensuring the `completedAt` field indicates it was never finished.

**可能的 follow-up**:
- How could you optimize the lookup complexity for `completeTask` from O(K) to O(1)?
- How would you ensure thread-safety in a concurrent implementation?
- What database schema changes would support persistence of this state?

---

来源：[DrustZ / Mingrui Zhang · online_resource/question-bank/hack2hire-premium.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/question-bank/hack2hire-premium.md)。作者整理资料；许可和第三方来源范围见阅读指南。
