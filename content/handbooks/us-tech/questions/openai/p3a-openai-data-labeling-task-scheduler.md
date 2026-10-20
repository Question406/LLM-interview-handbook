---
id: p3a-openai-data-labeling-task-scheduler
section: openai
order: 611
level: A
title: "OpenAI：人工标注调度：公平、唯一性与增量约束"
quick: "先把每条公平和不重复约束写成可检查的不变量，再看简单轮转能否满足；约束更复杂时可能需要二分图匹配或流模型。"
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - Coding
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · data-labeling-task-scheduler"
    url: https://www.1point3acres.com/interview/problems/company/openai/data-labeling-task-scheduler
    type: secondary
---

## 题目

给定一批任务、若干个模型和若干名人工标注员，为每个任务的每个模型输出分配一名标注员，生成 (task, model, human) 三元组，要满足题目给出的公平性和不重复约束。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先把每条约束写成一个能用代码检查的不变量，比如「每个 (任务, 模型) 恰好分配一次」「同一任务里标注员不重复」「标注员之间的负载差不超过某个值」。有了这些检查，再想怎么构造。

约束比较简单时，轮转就够了：任务 t 上的模型 m 交给第 $(t + m) \bmod H$ 号标注员，H 是标注员人数。约束变复杂时，比如某些标注员不能标某些模型、每人每天有容量上限、要求负载严格相差不超过 1，轮转就不一定满足了，可能要建成二分图匹配或者最小费用流来解。

生成之后，要用前面写好的不变量逐条检查：每个人的负载、每种组合出现的次数、任务是否全部覆盖。还要注意，不要只看题目名字就假设每个任务都要用上全部模型和全部标注员，先问清楚。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `schedule(tasks, models, humans, start_task=0)`：返回 (task, model, human) 三元组列表。每个任务要给每个模型恰好分配一次，同一任务内标注员不能重复。
- 分配规则固定为：任务 t 上的模型 m 交给 `(t + m) % humans` 号标注员。
- 需要 `humans >= models`，`tasks >= 0`，`models >= 1`，`start_task >= 0`，否则抛 `ValueError`。输出不超过 $10^6$ 条。
- 标注员之间的负载差不超过 `models`。这个构造不保证差值总能做到 1 以内。
- 流式变体：`start_task` 是起始任务编号，分批调用拼起来要和一次调用的结果完全相同。

### 输入输出示例

```text
schedule(2, 2, 3)  -> [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 2)]
schedule(3, 2, 3) + schedule(4, 2, 3, start_task=3) == schedule(7, 2, 3)
```

### 解题思路与正确性

同一任务内，m 取 $0, 1, \dots, M - 1$，而 $M \le H$，所以 $(t + m) \bmod H$ 是 M 个连续的余数，互不相同，标注员不会重复。

负载方面，固定一个模型 m，它在连续任务上分到的标注员也是一段连续的轮转，每名标注员被分到的次数最多相差 1。M 个模型叠加起来，负载差最多是 M。

流式调用时，任务编号接着上一批继续往下数，不在每批开始时重置为 0，所以分批结果和一次性结果完全一样。

### 完整参考实现（Python 3）

```python
def schedule(tasks, models, humans, start_task=0):
    """为每个任务的每个模型输出分配一名标注员，返回 [(task, model, human), ...]。

    任务 t 上模型 m 的输出交给 (t + m) % humans 号标注员。
    start_task 用于分批调用：先排 [0, 3) 再从 3 开始排，结果和一次排完相同。
    """
    if tasks < 0:
        raise ValueError(f"tasks must be >= 0, got {tasks}")
    if models < 1:
        raise ValueError(f"models must be >= 1, got {models}")
    if humans < models:
        raise ValueError(f"need at least as many humans as models ({humans} < {models})")
    if start_task < 0:
        raise ValueError(f"start_task must be >= 0, got {start_task}")

    assignments = []
    for task in range(start_task, start_task + tasks):
        # 同一任务内 m 取 0..models-1，且 models <= humans，所以 (task + m) % humans 互不相同
        for model in range(models):
            assignments.append((task, model, (task + model) % humans))
    return assignments
```

### 可执行测试

```python
from collections import Counter

assert schedule(2, 2, 3) == [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 2)]

# 小范围穷举检查三条不变量
humans = 5
for tasks in range(10):
    for models in range(1, 5):
        result = schedule(tasks, models, humans)

        # 每个 (任务, 模型) 恰好分配一次
        pairs = {(task, model) for task, model, _ in result}
        assert len(pairs) == tasks * models
        assert len(result) == tasks * models

        # 同一任务内标注员不重复
        for task in range(tasks):
            assert len({h for t, _, h in result if t == task}) == models

        # 标注员之间的负载差不超过 models
        counts = Counter(h for _, _, h in result)
        loads = [counts[h] for h in range(humans)]
        assert max(loads) - min(loads) <= models

# 分批调用和一次调用结果一致
assert schedule(3, 2, 3) + schedule(4, 2, 3, 3) == schedule(7, 2, 3)
```

### 复杂度与追问

设任务数为 T、模型数为 M。时间和输出空间都是 O(TM)。

如果追问「每个人的负载差必须不超过 1」：可以不按 (t + m) 轮转，而是用一个全局计数器，按 (任务, 模型) 的顺序依次取下一个标注员；只要 $M \le H$，同一任务里连续的 M 个编号仍然互不相同，全局负载差也能控制在 1 以内。

如果追问加入「某些标注员不能标某个模型」或「每人每天有容量上限」：这时轮转构造不再适用，要建成二分图，用匹配或最小费用流求解，并说明这份构造不是所有公平约束的通解。
