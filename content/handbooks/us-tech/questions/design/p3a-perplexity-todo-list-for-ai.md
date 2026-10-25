---
id: p3a-perplexity-todo-list-for-ai
section: design
order: 601
level: A
title: "Perplexity：AI ToDoList：依赖、就绪与失败传播"
quick: "同时维护任务依赖和反向依赖图：所有前置完成才就绪，完成时检查直接后继，失败时沿反向边传播到全部未结束后代。只允许依赖已有任务可保证无环；若允许补加边，就要逐次做环检测。"
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · todo-list-for-ai"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/todo-list-for-ai
    type: secondary
---

## 题目描述

实现带依赖关系的 AI 任务清单。任务完成或失败时，其后续任务的可执行状态应按依赖关系变化。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `Tasks()` 创建空清单；`add(task_id,depends=())` 添加唯一 id，只依赖已经存在的任务，因此依赖图无环。没有依赖或依赖均 done 时初始 ready；任一依赖 failed 时初始 failed；否则 blocked。
- `start(task_id)` 使 ready 任务变成 running；`finish(task_id,success=True)` 结束 running 任务。成功变成 done，直接后继若全部依赖 done 则变成 ready；失败变成 failed，所有尚未结束的后代变成 failed，已经 done 的节点不变。
- `snapshot() -> dict` 返回 id 到 ready/blocked/running/done/failed 字符串的映射。
- 输入保证任务名唯一、依赖存在，start/finish 符合合法状态；最多10000任务，无需额外非法调用校验。

### 输入输出示例

```text
add("a"); add("b", ["a"]); add("c", ["b"])
start("a"); finish("a"); snapshot()   -> {"a": "done", "b": "ready", "c": "blocked"}
start("b"); finish("b", False)        -> c 变为 "failed"，a 仍是 "done"
add("d", ["b"])                       -> d 一开始就是 "failed"
```

## 解题思路与参考答案

## 题目

给 AI agent 设计一个 ToDo 列表：先实现任务的基本状态流转（待做、进行中、完成），再加上任务之间的依赖关系，并且在某个任务失败时，把依赖它的下游任务级联标记为失败。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

我会同时维护两张图：正向记录每个任务依赖谁，用来判断是否能开始；反向记录谁依赖它，用来通知下游。所有依赖都完成，任务才从 blocked 变成 ready。

例如 a → b → c，a 完成时只需检查 b，c 还要等 b 真正完成。失败则不同：要沿反向边遍历全部后代，把尚未结束的任务标记为 failed；菱形依赖可能多次到达同一后代，用 visited 去重，已经完成的任务保留结果。

这份练习只允许新任务依赖已存在任务，因此添加顺序就是拓扑序，图天然无环。若改成给已有任务补边，每次都要检查是否成环。动手前还要确认失败重试成功后，级联失败的下游是否恢复，以及“父子任务”是否就是依赖关系。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Tasks.add(task_id, depends=())`：添加任务，只能依赖已存在的任务，因此依赖图是 DAG。没有依赖或依赖都已完成时初始为 `ready`，有依赖已失败时初始为 `failed`，否则为 `blocked`。重复 id 或依赖不存在抛 `ValueError`。
- `start(task_id)`：只有 `ready` 的任务能开始，变为 `running`。
- `finish(task_id, success=True)`：只有 `running` 的任务能结束。成功变为 `done`，并让所有依赖都已 `done` 的直接后继变成 `ready`；失败变为 `failed`，所有还没结束的后代都变成 `failed`。已经 `done` 的任务不会被改成失败。
- `snapshot() -> dict`：返回每个任务的当前状态。
- 状态不对或任务不存在时抛 `ValueError`。最多 $10^4$ 个任务。

### 输入输出示例

```text
add("a"); add("b", ["a"]); add("c", ["b"])
start("a"); finish("a"); snapshot()   -> {"a": "done", "b": "ready", "c": "blocked"}
start("b"); finish("b", False)        -> c 变为 "failed"，a 仍是 "done"
add("d", ["b"])                       -> d 一开始就是 "failed"
```

### 解题思路与正确性

一个任务变成 ready 的条件是「所有依赖都 done」，而依赖变成 done 只发生在 `finish` 里，所以每次 `finish` 成功后只检查它的直接后继就够了：更远的后继总是经过某个直接后继才连到这个任务，而那个直接后继此刻最多是 ready，还没有 done，所以更远的后继不可能在这一步满足条件。

失败传播用栈做 DFS，`seen` 保证每个后代只处理一次，菱形依赖也不会重复。因为任务只能依赖已存在的任务，添加顺序就是拓扑序，不需要再做环检测。

### 完整参考实现（Python 3）

```python
class Tasks:
    """带依赖的任务列表。状态：blocked -> ready -> running -> done / failed。

    只能依赖已经存在的任务，所以依赖图天然无环，添加顺序就是一个拓扑序。
    """

    def __init__(self):
        self.state = {}     # task_id -> 状态字符串
        self.deps = {}      # task_id -> 它依赖的任务集合
        self.children = {}  # task_id -> 直接依赖它的任务集合（反向边）

    def _require(self, task_id):
        if task_id not in self.state:
            raise ValueError(f"unknown task: {task_id!r}")

    def _initial_state(self, deps):
        if any(self.state[dep] == "failed" for dep in deps):
            return "failed"
        if all(self.state[dep] == "done" for dep in deps):
            return "ready"
        return "blocked"

    def add(self, task_id, depends=()):
        if task_id in self.state:
            raise ValueError(f"duplicate task: {task_id!r}")
        for dep in depends:
            self._require(dep)
        deps = set(depends)
        self.state[task_id] = self._initial_state(deps)
        self.deps[task_id] = deps
        self.children[task_id] = set()
        for dep in deps:
            self.children[dep].add(task_id)

    def start(self, task_id):
        self._require(task_id)
        if self.state[task_id] != "ready":
            raise ValueError(f"task {task_id!r} is {self.state[task_id]}, not ready")
        self.state[task_id] = "running"

    def finish(self, task_id, success=True):
        self._require(task_id)
        if self.state[task_id] != "running":
            raise ValueError(f"task {task_id!r} is {self.state[task_id]}, not running")
        if success:
            self.state[task_id] = "done"
            self._unblock_children(task_id)
        else:
            self.state[task_id] = "failed"
            self._fail_descendants(task_id)

    def _unblock_children(self, task_id):
        # 只需看直接后继：更远的后继至少还依赖一个没完成的直接后继
        for child in self.children[task_id]:
            if self.state[child] == "blocked" and all(
                self.state[dep] == "done" for dep in self.deps[child]
            ):
                self.state[child] = "ready"

    def _fail_descendants(self, task_id):
        # 菱形依赖里同一个后代会被多次碰到，用 seen 去重
        stack = list(self.children[task_id])
        seen = set()
        while stack:
            task = stack.pop()
            if task in seen:
                continue
            seen.add(task)
            if self.state[task] not in ("done", "failed"):
                self.state[task] = "failed"
            stack.extend(self.children[task])

    def snapshot(self):
        return dict(self.state)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert tasks.snapshot() == {"a": "done", "b": "ready", "c": "blocked"}` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 链式依赖 a -> b -> c：a 完成后只有 b 变 ready
tasks = Tasks()
tasks.add("a")
tasks.add("b", ["a"])
tasks.add("c", ["b"])
tasks.start("a")
tasks.finish("a")
assert tasks.snapshot() == {"a": "done", "b": "ready", "c": "blocked"}

# b 失败，下游 c 级联失败，已完成的 a 不受影响
tasks.start("b")
tasks.finish("b", False)
assert tasks.snapshot()["c"] == "failed"
assert tasks.snapshot()["a"] == "done"

# 依赖已失败任务的新任务直接是 failed
tasks.add("d", ["b"])
assert tasks.snapshot()["d"] == "failed"

# 菱形依赖：两个前置都完成后汇合点才 ready
tasks = Tasks()
tasks.add("root")
tasks.add("left", ["root"])
tasks.add("right", ["root"])
tasks.add("join", ["left", "right"])
tasks.start("root")
tasks.finish("root")
tasks.start("left")
tasks.finish("left")
assert tasks.snapshot()["join"] == "blocked"
tasks.start("right")
tasks.finish("right")
assert tasks.snapshot()["join"] == "ready"

# 非法操作
expect_value_error(tasks.add, "root")              # 重复 id
expect_value_error(tasks.add, "x", ["missing"])    # 依赖不存在
expect_value_error(tasks.start, "root")            # 已完成的任务不能再 start
expect_value_error(tasks.finish, "join")           # ready 还没 start
expect_value_error(tasks.start, "missing")         # 未知任务
```

### 复杂度与追问

设任务数为 V、依赖边数为 E。`add` 是 O(该任务的依赖数)；成功的 `finish` 是 O(直接后继的依赖数之和)；失败的 `finish` 是 O(后代节点数 + 后代之间的边数)；`snapshot` 是 O(V)。

- 重试：不能简单地把 failed 改回 ready。被级联失败的下游要重新计算状态，最好给每次失败记一个原因（是自己失败还是被上游拖累），重试时只恢复因这个上游失败的任务。
- 动态补加依赖：给已有任务加边前，要检查新依赖是否已经能从这个任务沿反向边走到（DFS 或 BFS），能走到就会成环，应该拒绝。加边后还要重新计算这个任务的状态，比如 ready 的任务多了一个没完成的依赖就要退回 blocked。
- 撤销已完成的任务：下游已经开始甚至完成的任务要怎么处理需要另外定义，通常要给状态加版本号来判断哪些结果已经过期。
