---
id: p3a-cohere-terminal-game-llm-agent
section: overview
order: 805
level: A
title: Cohere：把终端游戏启发式实现替换成 LLM Agent
quick: 先读懂游戏的观察、动作和胜负规则，把原启发式玩家当基线；LLM 只返回结构化动作，程序校验合法性，失败时退回启发式，并用固定种子多局对比胜率。
companies:
  - cohere
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - cohere
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · Cohere：把终端游戏启发式实现替换成 LLM Agent
    url: >-
      https://www.1point3acres.com/interview/problems/d363b064-b6f5-4efb-afd2-03b807fa85ff
    type: secondary
---

## 题目描述

实现一个供终端游戏等工具环境使用的模型代理循环，以及固定案例评估器。使用脚本模型和注入工具，不需要外部 LLM 服务。

以下为手册重构练习约定。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `run_agent(model,tools,goal,budget=8) -> (answer,messages)`，budget>=1；tools 是名称到可用函数的映射，工具由关键字参数调用。model 是接收消息列表、返回动作字典的注入函数。
- 工具动作字段为 type="tool"、name（工具名字符串）、args（可 JSON 序列化字典）、id（非空字符串）；最终动作字段为 type="final"、answer（字符串）。本题使用脚本模型，不调用外部服务，也不执行模型输出代码。
- 历史初始为 [{"role":"user","content":goal}]；每次模型动作追加 {"role":"assistant","content":action}。工具调用后追加 {"role":"tool","content":result}；成功 result 为 {"ok":True,"value":返回值}，失败为 {"ok":False,"error":错误字符串}。final 直接返回答案及包含该 final 动作的历史。
- 同一 id 的相同 name/args 只调用一次工具，之后复用完整 result（参数字典顺序不影响相等）；同一 id 换参数、未知工具或不合协议的动作返回失败 observation。工具异常也变为失败 result，error 含异常类名与消息。预算内未产生 final 时以 RuntimeError 报告预算耗尽。
- `evaluate(cases,predict) -> dict`：cases 是 (question,expected) 列表，严格比较 predict(question) 与 expected，返回 {"accuracy":正确数/总数,"failures":[(index,expected,actual)]}。空案例 accuracy=0.0；predict 异常的 actual 为 {"error":异常类名}。

### 输入输出示例

```text
模型第 1 步：{"type": "tool", "name": "add", "args": {"a": 2, "b": 3}, "id": "x"}  -> 执行 add，回填 {"ok": True, "value": 5}
模型第 2 步：同一个动作，id 还是 "x"                                       -> 不再执行，回填同一结果
模型第 3 步：{"type": "final", "answer": "5"}                              -> 返回 ("5", messages)
```

整个过程中 `add` 实际只被调用一次。

## 解题思路与参考答案

## 题目

给一个几百行的 Python 终端游戏，里面已有基于启发式规则的玩家实现。要求在限定时间内写一个新的、由 LLM 驱动的 agent 替换它来玩这个游戏。

> 来源：一亩三分地 Cohere 题目详情页（2026-10-18 读取），读了网站的题目详情，但题面是网站从面经整理的；网站收录也不等于公司官方确认。下面的接口、约束和测试是手册补的练习约定。

## 思路

我会先读懂观察、合法动作和胜负规则，保留原启发式玩家作基线，再接入只返回结构化动作的 LLM。比如模型给出非法动作，程序要拒绝、回填错误，重试用完后退回原策略，不能让一局游戏卡住。效果用固定种子的多局胜率与基线对比。

接着把 LLM 包成一个结构化的决策函数：把当前观察整理成 prompt，要求模型返回固定格式的动作，程序再检查动作是否合法。模型输出格式错误或给出非法动作时，可以把错误告诉模型让它重试；重试次数用完就退回启发式策略，保证游戏不会卡住。

最后要能说明效果：固定随机种子跑多局，记录每局轨迹和胜率，与启发式基线对比。面试里能稳定复现、可以验证的结果，比展示一次碰巧赢的对局更有说服力。工具和 API 的使用规则以面试当时的说明为准。

下面的练习把这套做法抽象成通用的工具调用循环：游戏动作可以看作工具，合法性检查就是动作校验。

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

**模型一直给非法动作怎么办？**
把具体错误回填给模型，限定重试次数；超过次数就调用原来的启发式策略选动作，并在轨迹里记下这次退回，评估时单独统计。
**怎么证明 LLM agent 比启发式更好？**
固定一组随机种子，两种策略各跑同样的局数，比较胜率和平均得分，并抽查失败局的轨迹找原因。
**进程崩溃后还能保证每个工具只执行一次吗？**
不能。`results_by_id` 只在内存里，生产版要把调用状态持久化，或者让工具本身接受 idempotency key。
