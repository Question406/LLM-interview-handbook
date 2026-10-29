---
id: p3a-apple-task-dag-code
section: tech-screen
order: 81
level: S
title: 一亩三分地 Apple AIML Infra：补全有依赖的面向对象 task pipeline
quick: >-
  用任务 ID
  保存函数和依赖，用入度与后继表做拓扑执行。一个任务只在全部前驱完成后计算，依赖结果按声明顺序传入；共享上游任务每次运行只执行一次，不能用递归重复计算整棵依赖树。
companies:
  - apple
tags:
  - 一亩三分地继续检索
  - Apple
  - AFM 专项 2026-10
  - 一亩三分地
  - 完整编程练习
  - DAG
realInterview: true
status: published
format: markdown
collapseAnswer: true
updatedAt: 2026-10-26T00:00:00.000Z
sources:
  - title: 苹果AIML infra engr全套（候选人原帖）
    url: 'https://www.1point3acres.com/bbs/thread-1149108-1-1.html'
    type: interview
  - title: Python graphlib — TopologicalSorter
    url: 'https://docs.python.org/3/library/graphlib.html'
    type: primary
---

## 题目描述

**source attribution 与适用范围：**2026-10-26 经 Chrome 核对，原帖发布于 2025-10-07 14:14:15。作者报告 Apple AIML Infra onsite 中给出类似 Airflow 的不完整面向对象任务 pipeline，要补全添加任务与计算全部结果的 API，任务存在依赖，面试中确认是 DAG 并使用拓扑排序。原始类定义、函数签名、错误处理与测例没有披露；不是已确认的 AFM 团队题。

以下接口与约束是手册重构练习约定，建议限时 30 分钟。

### 输入与接口

实现类 `TaskPipeline`，初始无任务：

- `add_task(name, fn, dependencies=())`：name 为唯一非空字符串；fn 为可调用对象，接收各依赖结果作为位置参数，顺序与 dependencies 一致；dependencies 为不重复的任务名称序列。添加时依赖可以尚未注册，但 `run_all` 前都会注册。
- `run_all()`：计算并返回本次所有任务结果。

### 输出与约束

保证输入形成有向无环图，依赖存在、任务名无重复，fn 不修改 pipeline 且不会抛异常。每个任务在一次 run_all 中恰好执行一次，包括没有后继的任务；返回 `任务名 -> 结果` 字典，不要求字典键的顺序。空 pipeline 返回空字典。多次调用 run_all 必须重新计算，不能复用上次结果。

允许依赖分支共享上游节点；不要直接递归展开导致同一前驱执行多次。复杂度应为任务数与依赖边数的线性量级，不包含 fn 本身的计算成本。不要求并行调度、失败重试或持久化。

### 示例

```text
load() -> 3
left(load_result) -> load_result+1
right(load_result) -> load_result*2
merge(left_result,right_result) -> left_result+right_result
run_all() -> {'load':3,'left':4,'right':6,'merge':10}
其中load只执行一次。
```

## 解题思路与参考答案

添加任务时保存配置，不立即运行。每次 run_all 建立新的入度、后继表与结果字典。入度是尚未完成的前驱数量；初始零入度任务可执行，完成后释放其后继。

```python
from collections import deque


class TaskPipeline:
    def __init__(self):
        self.tasks = {}

    def add_task(self, name, fn, dependencies=()):
        self.tasks[name] = (fn, tuple(dependencies))

    def run_all(self):
        indegree = {name: len(deps) for name, (_, deps) in self.tasks.items()}
        successors = {name: [] for name in self.tasks}
        for name, (_, dependencies) in self.tasks.items():
            for dependency in dependencies:
                successors[dependency].append(name)
        ready = deque(name for name in self.tasks if indegree[name] == 0)
        results = {}
        while ready:
            name = ready.popleft()
            fn, dependencies = self.tasks[name]
            results[name] = fn(*(results[dep] for dep in dependencies))
            for child in successors[name]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    ready.append(child)
        return results
```

每条边只处理一次，调度时间与空间为 $O(V+E)$，另加结果对象和任务计算的成本。本题保证 DAG；若扩展为接受一般图，要在产生外部副作用前做完整环检测，而不是只在执行一半后发现未完成任务。

## 简单测试怎么写

把实现和测试依次放入 `solution.py`，运行 `python3 solution.py`，只依赖标准库。用菱形依赖验证共享节点只运行一次，再检查依赖参数顺序、后注册依赖、多次运行和独立任务。

```python
calls = []


def load():
    calls.append('load')
    return 3


pipeline = TaskPipeline()
pipeline.add_task('merge', lambda a, b: a + b, ('left', 'right'))
pipeline.add_task('left', lambda value: value + 1, ('load',))
pipeline.add_task('right', lambda value: value * 2, ('load',))
pipeline.add_task('load', load)
assert pipeline.run_all() == {'load': 3, 'left': 4, 'right': 6, 'merge': 10}
assert calls == ['load']
assert pipeline.run_all()['merge'] == 10
assert calls == ['load', 'load']
ordered = TaskPipeline()
ordered.add_task('a', lambda: 2)
ordered.add_task('b', lambda: 7)
ordered.add_task('subtract', lambda x, y: x - y, ('b', 'a'))
ordered.add_task('independent', lambda: 99)
assert ordered.run_all()['subtract'] == 5
assert ordered.run_all()['independent'] == 99
assert TaskPipeline().run_all() == {}
```

## 面试追问

**任务失败后能重试吗？** 先定义函数是否有副作用，以及重复调用能否识别同一逻辑操作。纯计算可以重试；写入外部系统要结合 idempotency key、事务或结果查询，不能把一次调度当成恰好一次外部执行。

**怎样并行？** 将 ready 队列交给受控 executor，只在任务真正成功完成后减少后继入度。需要限制并发、处理结果提交并保护共享状态，不能在任务刚提交时就放行下游。

**怎样接到 data pipeline？** 可以把抽取、过滤、deduplication、分词与统计作为节点，传递不可变数据分片的引用，而不是把十亿条文档全部塞进结果字典。生产版本还需关联输入版本与产物清单。
