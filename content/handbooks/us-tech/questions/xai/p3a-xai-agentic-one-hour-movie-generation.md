---
id: p3a-xai-agentic-one-hour-movie-generation
section: xai
order: 622
level: S
title: "xAI：一小时电影生成 Agent workflow"
quick: "我会把一小时电影分成剧本、分镜、素材、镜头生成、剪辑和评审，每个阶段保存产物。角色和场景从同一份设定库取条件，失败按镜头重试，高成本阶段前人工审批；编排循环还要校验工具调用、去重并限制步数。"
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · agentic-one-hour-movie-generation"
    url: https://www.1point3acres.com/interview/problems/company/xai/agentic-one-hour-movie-generation
    type: secondary
---

## 题目描述

为代理式内容生成流程实现可本地运行的工具执行骨架。本练习使用模拟模型及工具，不要求调用真实电影生成服务。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

`run_agent(model, tools, goal, budget=8)` 返回 `(answer, messages)`。tools 是工具名称到可调用函数的白名单映射，model 接收当前 messages，返回工具动作 `{"type":"tool","name":名称,"args":参数字典,"id":非空字符串}`，或最终动作 `{"type":"final","answer":字符串}`。messages 以包含 goal 的 user 消息开始，保留每次 assistant 动作、对应 tool 观测以及最终动作。

工具成功观测包含 `{"ok":True,"value":结果}`。未知工具、格式错误、工具异常和同一 id 对应不同调用的情况，应作为失败观测反馈给模型。相同 id、相同工具及参数的重复调用复用已有结果，不能重复执行工具。每次请求模型消耗一次预算；预算用尽仍无 final 时抛出 RuntimeError。

另实现 `evaluate(cases, predict)`，cases 为 `(question,expected)` 列表，调用 predict(question)，对预测和期望做严格相等比较，返回 `{"accuracy":准确率,"failures":[(索引,期望,实际),...]}`；空用例集合准确率为 0。测试不需要外部模型或真实网络。

### 示例

```text
模拟模型依次返回：调用 add(a=2,b=3,id="x")、重复同一调用、final(answer="5")。
工具 add 返回 5。
run_agent 返回 answer="5"；add 实际执行 1 次，两条工具观测都包含结果 5。
```

## 解题思路与参考答案

我会把电影拆成可保存、可局部重试的镜头流水线，再用全局设定库约束前后一致。例如同一个角色换镜头后衣服变了，或者天色接不上，就只重生成有问题的那一段，不必重做整部电影。

## 题目

开放式设计题：设计一个 agent workflow，自动生成约一小时长的电影，重点是怎样拆分任务、组织生成过程，以及让整部片子前后保持一致。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

一小时视频需要分阶段生成。我会先定剧本和分镜，再准备角色设定、场景参考等素材，逐镜头生成后做剪辑合成和评审。每个阶段的产物都保存下来，下一阶段直接使用，失败时也有恢复点。

一致性是这道题的难点。要维护一份全局「设定库」：角色外貌、服装、场景布局、时间线。每个镜头生成时都带上相关设定，生成后检查是否违背，比如角色换了衣服、天色和上一个镜头接不上。

失败处理按镜头粒度做：某个镜头不合格就只重生成这一段，不推倒整部片子。剧本定稿、最终剪辑这类代价高的阶段前，安排人工审批。

评估要具体：叙事是否连贯、画面和声音是否连续、总成本和生成时长各是多少。只列出要用哪些模型，答不出这些问题。

下面的练习只实现编排的核心，也就是一个带校验、去重和步数上限的工具调用循环。生成剧本、生成镜头都可以看作循环里的工具。完整的电影系统还需要下面「追问」里提到的那些部分。

相关题：[[p3a-anthropic-agents-coding-llm-tool-use]]（同一份代码，题目是通用的工具调用 agent）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `run_agent(model, tools, goal, budget=8) -> (answer, messages)`：`model(messages)` 每次返回一个 JSON 对象，只能是两种之一：`{"type": "tool", "name", "args", "id"}` 请求调用工具，或 `{"type": "final", "answer"}` 给出最终答案。`tools` 是工具名到函数的字典。
- `args` 必须是 dict，`id` 必须是非空字符串，`answer` 必须是字符串。模型返回的代码不会被自动执行。
- 同一个 `id` 的同一调用只执行一次，重复请求直接复用结果；同一个 `id` 换了工具名或参数则拒绝。
- 未知工具、格式非法的动作和工具抛出的异常都不让循环崩溃，而是作为一条 `tool` 消息回填给模型。`budget` 步内没拿到 final 就抛 `RuntimeError`。
- `evaluate(cases, predict)`：对固定的 `(question, expected)` 案例严格比较，返回 `accuracy` 和失败列表 `(下标, 期望, 实际)`。
- 测试用写死动作序列的脚本模型，不需要调外部 API。

### 输入输出示例

```text
模型第 1 步：{"type": "tool", "name": "add", "args": {"a": 2, "b": 3}, "id": "x"}  -> 执行 add，回填 {"ok": True, "value": 5}
模型第 2 步：同一个动作，id 还是 "x"                                       -> 不再执行，回填同一结果
模型第 3 步：{"type": "final", "answer": "5"}                              -> 返回 ("5", messages)
```

整个过程中 `add` 实际只被调用一次。

### 解题思路与正确性

工具循环先用 `validate_action` 检查动作格式，再检查工具白名单，通过后才执行。模型写错字段或编出不存在的工具时，循环回填错误 observation，让它下一步修改，不会直接把生成内容当代码运行。

去重靠 `results_by_id`：键是模型给的 call id，值是调用签名和结果。签名用 `json.dumps(..., sort_keys=True)` 生成，所以参数顺序不同的同一调用会被认成同一个。成功和失败的结果都会缓存，重试同一个 id 不会再触发一次副作用。同一个 id 配了不同参数时明确拒绝，避免把旧结果错当成新调用的答案。

`budget` 限制总步数，保证模型陷入重复调用时循环也会结束。`evaluate` 用固定案例集打分，改 prompt 前后跑同一组案例，才能看出改动到底有没有用。

### 完整参考实现（Python 3）

```python
import json


def validate_action(action):
    """检查模型输出的动作格式，不合法时抛 ValueError。"""
    if not isinstance(action, dict):
        raise ValueError("action must be a JSON object")
    if action.get("type") == "final":
        if not isinstance(action.get("answer"), str):
            raise ValueError("final answer must be a string")
        return
    if action.get("type") != "tool":
        raise ValueError("action type must be 'tool' or 'final'")
    if not isinstance(action.get("args"), dict):
        raise ValueError("tool args must be an object")
    call_id = action.get("id")
    if not isinstance(call_id, str) or not call_id:
        raise ValueError("tool call id must be a non-empty string")


def call_tool(tools, name, args):
    """执行白名单里的工具；工具自己抛出的异常转成失败结果，不中断循环。"""
    try:
        return {"ok": True, "value": tools[name](**args)}
    except Exception as error:
        return {"ok": False, "error": f"{type(error).__name__}: {error}"}


def run_agent(model, tools, goal, budget=8):
    """让 model 逐步提议动作，最多 budget 步；返回 (answer, messages)。

    同一个 call id 只执行一次工具：重复请求直接复用缓存结果，
    同一个 id 换了工具名或参数则拒绝。
    """
    if budget < 1:
        raise ValueError("budget must be at least 1")
    messages = [{"role": "user", "content": goal}]
    results_by_id = {}  # call id -> (调用签名, 结果)

    for _ in range(budget):
        action = model(list(messages))  # 传副本，模型改不了真实历史
        messages.append({"role": "assistant", "content": action})
        try:
            validate_action(action)
            if action["type"] == "final":
                return action["answer"], messages

            name, args, call_id = action.get("name"), action["args"], action["id"]
            if name not in tools:
                raise ValueError(f"unknown tool: {name!r}")
            # sort_keys 让参数顺序不同的同一调用得到同一个签名
            signature = json.dumps([name, args], sort_keys=True, allow_nan=False)
            if call_id in results_by_id:
                cached_signature, result = results_by_id[call_id]
                if cached_signature != signature:
                    raise ValueError(f"conflicting reuse of call id {call_id!r}")
            else:
                result = call_tool(tools, name, args)
                results_by_id[call_id] = (signature, result)
        except (ValueError, TypeError) as error:
            # 格式错误也作为 observation 回填，让模型下一步有机会改正
            result = {"ok": False, "error": str(error)}
        messages.append({"role": "tool", "content": result})

    raise RuntimeError("step budget exhausted")


def evaluate(cases, predict):
    """对固定案例严格比较 predict(question) == expected，返回准确率和失败列表。"""
    failures = []
    for index, (question, expected) in enumerate(cases):
        try:
            actual = predict(question)
        except Exception as error:
            actual = {"error": type(error).__name__}
        if actual != expected:
            failures.append((index, expected, actual))
    accuracy = 1 - len(failures) / len(cases) if cases else 0.0
    return {"accuracy": accuracy, "failures": failures}
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert answer == "5"` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def scripted_model(actions):
    remaining = iter(actions)
    return lambda messages: next(remaining)

# 同一个 id 请求两次，工具只执行一次
calls = []

def add(a, b):
    calls.append((a, b))
    return a + b

add_call = {"type": "tool", "name": "add", "args": {"a": 2, "b": 3}, "id": "x"}
model = scripted_model([add_call, add_call, {"type": "final", "answer": "5"}])
answer, trace = run_agent(model, {"add": add}, "2+3")
assert answer == "5"
assert calls == [(2, 3)]
assert trace[2] == {"role": "tool", "content": {"ok": True, "value": 5}}
assert trace[4] == trace[2]

# 同一个 id 换了参数：拒绝，并作为 observation 回填
changed_call = dict(add_call, args={"a": 1, "b": 1})
model = scripted_model([add_call, changed_call, {"type": "final", "answer": "done"}])
answer, trace = run_agent(model, {"add": add}, "2+3")
assert trace[4]["content"]["ok"] is False
assert "conflicting" in trace[4]["content"]["error"]

# 工具抛异常也变成失败结果，循环继续
def broken():
    raise KeyError("missing")

broken_call = {"type": "tool", "name": "broken", "args": {}, "id": "b"}
model = scripted_model([broken_call, {"type": "final", "answer": "gave up"}])
answer, trace = run_agent(model, {"broken": broken}, "x")
assert answer == "gave up"
assert trace[2]["content"]["error"].startswith("KeyError")

# 未知工具一直重复，步数用完抛 RuntimeError
unknown_call = {"type": "tool", "name": "nope", "args": {}, "id": "x"}
try:
    run_agent(lambda messages: unknown_call, {}, "x", 2)
except RuntimeError:
    pass
else:
    raise AssertionError("budget should be exhausted")

# 固定评测集
assert evaluate([("a", "A"), ("b", "B")], str.upper)["accuracy"] == 1
report = evaluate([("a", "A"), ("b", "x")], str.upper)
assert report["accuracy"] == 0.5
assert report["failures"] == [(1, "x", "B")]
```

### 复杂度与追问

设步数上限为 B。循环最多调用 B 次模型和至多 B 次工具，总耗时基本由模型和工具本身决定；消息历史和缓存都是 O(B)。

- 一个循环怎么撑起整部电影？不能只靠它。实际系统要先把影片规划成一张镜头 DAG：节点是镜头或场景，边表示依赖（比如同一场景的镜头要共用设定）。调度器按 DAG 并行生成，每个节点内部才是这样的工具调用循环。
- 角色前后长得不一样怎么办？给每个角色固定参考图和文字设定，生成时作为条件输入；生成后用人脸或外观相似度检查，不合格的镜头局部重试。
- 进程崩溃后会重复生成很贵的镜头吗？练习里的缓存只在内存，会丢。生产版要把每个镜头的状态和产物持久化，重启后跳过已完成的节点。
