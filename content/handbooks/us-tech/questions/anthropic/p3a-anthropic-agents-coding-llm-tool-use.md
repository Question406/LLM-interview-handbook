---
id: p3a-anthropic-agents-coding-llm-tool-use
section: anthropic
order: 604
level: S
title: Anthropic：用 LLM 构造多步工具 Agent
quick: >-
  我会写一个由程序控制的工具循环：模型每步给出结构化动作，程序校验后执行白名单工具，再把结果回填。call id
  用来避免重复执行，步数上限用来保证循环能结束，完整轨迹则留给调试和评估。
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Anthropic
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · Anthropic · agents-coding-llm-tool-use
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/agents-coding-llm-tool-use
    type: secondary
---

## 题目描述

实现一个可在本地用模拟模型和工具测试的代理执行器，支持工具调用、重试观测和明确的执行预算。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

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

## 题目

在 Colab 里用给定的 LLM API 写一个会调用工具的 agent：把 prompt 发给模型，解析模型想调用的工具，执行后把结果放回上下文，直到模型给出最终答案。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。下面的接口、约束和测试是手册补的练习约定。

## 思路

我会让程序控制整个循环，模型每步只提出一个结构化动作：调用工具，或者给出最终答案。程序把完整对话交给模型，收到动作后先校验，再执行工具，把结果作为新消息追加回对话。这样 execution constraints 和每一步发生了什么都能看清楚。

几个容易被问到的点：

- 模型输出不可信。先检查 JSON 格式和字段，工具名只能来自白名单，参数类型不对就把错误回填给模型，而不是让程序崩溃。
- 工具调用要能安全重试。给每次调用一个 id，同一个 id 只执行一次，这样模型重复请求或网络重试都不会让副作用发生两次。
- 必须有步数上限，否则模型反复调用同一个工具时循环永远不会结束。
- 记录完整轨迹，方便重放、调试和评分。

先让最小 feedback loop 跑通一个简单任务，再加重试和错误恢复。具体的 API 形式、可用工具和任务内容以面试时给的说明为准。

相关题：[[p3a-anthropic-prompting-engineering-with-llms]]（同一份代码里的 `evaluate` 部分，重点是用固定案例集评估 prompt）。

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

模型的输出只是一个提议。循环先用 `validate_action` 检查格式，再确认工具名在白名单里，最后才真正调用。这样模型写错字段或编造工具名时，最坏结果是收到一条错误 observation，不会执行意外的代码。

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

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

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

- 进程崩溃后还能保证每个工具只执行一次吗？不能。`results_by_id` 只在内存里，重启后就丢了。生产版要把调用状态持久化，执行有副作用的工具前先落一条「准备执行」记录，执行完再写结果，或者让工具本身接受 idempotency key。
- 消息越来越长怎么办？可以只保留最近几轮完整消息，把更早的工具结果压缩成摘要；大块结果存外部，消息里只放引用。
