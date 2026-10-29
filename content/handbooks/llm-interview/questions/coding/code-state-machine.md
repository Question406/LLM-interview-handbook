---
id: code-state-machine
section: coding
order: 9
level: A
title: 设计 Tool-Call State Machine：哪些状态不能交给 LLM 自己“记”？
quick: >-
  运行时要显式保存 PARSE→VALIDATE→AUTHORIZE→EXECUTE→OBSERVE→RETRY/FAIL→RETURN 这些状态，并把
  attempt、tool-call ID、权限和 side-effect status 持久化。重试次数、授权结果、副作用有没有发生，都由 harness
  记，模型从对话上下文里“记得”的不算数。
tags:
  - Agent
  - State Machine
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: OpenAI — A practical guide to building AI agents
    url: >-
      https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
    type: reference
  - title: MCP specification
    url: 'https://modelcontextprotocol.io/specification/2025-06-18'
    type: reference
---

## 题目描述

实现工具调用运行时的一个确定性状态转移函数，由程序保存重试预算。本题是独立状态表练习，不要求实现真实工具、持久化系统或图中所有扩展状态。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `step(state,event,ctx)`。state/event 为下列合法状态事件对；ctx 包含非负整数 attempts、`max_retry`，attempts 表示已经批准的重试次数。

### 输出与约束

转移为 PARSE+ok→VALIDATE，VALIDATE+ok→AUTHORIZE，VALIDATE+`bad_args`→REPAIR，AUTHORIZE+ok→EXECUTE，AUTHORIZE+deny→DENY，EXECUTE+ok→OBSERVE，RETRY+ok→EXECUTE，OBSERVE+ok→RETURN。EXECUTE+fail 在 attempts 小于`max_retry`时把 attempts 加1并返回 RETRY，否则返回 FAIL 且不加计数。其他转移不改 ctx；基础输入保证事件合法。

### 示例

```text
ctx={attempts:0,max_retry:1}
step("PARSE","ok",ctx) -> "VALIDATE"，attempts仍为0
step("EXECUTE","fail",ctx) -> "RETRY"，attempts变为1
再次step("EXECUTE","fail",ctx) -> "FAIL"，attempts仍为1
```

## 解题思路与参考答案

模型可以决定调不调工具、参数怎么填，但事务状态、权限、重试次数和已经产生的副作用，要由运行框架 harness 结构化保存。把 tool 调用进度写进对话、让模型「自己记得」，一压缩 context、一出 hallucination、一重启进程，这些安全信息就丢了。

比如一次转账工具调用超时了，模型看对话觉得「好像没成功」，就再发一次，结果钱转了两笔。状态机要做的，就是让这种情况只能走查状态那条路，没法盲目重发。

## 显式状态：PARSE 到 RETURN，失败有单独的边

主路径大概是这样：

```text
PARSE -> VALIDATE -> AUTHORIZE -> EXECUTE -> OBSERVE -> RETURN
              |             |            |
            REPAIR        DENY       RETRY / UNKNOWN
                                      |
                                    STATUS_CHECK
```

PARSE 把模型输出解析成结构化 call，带名字、参数和 id；VALIDATE 按 JSON schema 检查参数；AUTHORIZE 查权限策略，看是只读、写入还是要人工审核；EXECUTE 真正调工具；OBSERVE 把返回值整理成机器可读的 observation；RETURN 把结果交给模型或用户。失败的几条边各管各的：REPAIR 只修参数，不跳过授权；DENY 就是不执行；RETRY 受 `attempt` 上限约束；UNKNOWN / STATUS_CHECK 用在超时之后，拿 idempotency key 去查状态，别再发一次付款。

```python
TRANSITIONS = {
    ("PARSE", "ok"): "VALIDATE",
    ("VALIDATE", "ok"): "AUTHORIZE",
    ("VALIDATE", "bad_args"): "REPAIR",
    ("AUTHORIZE", "ok"): "EXECUTE",
    ("AUTHORIZE", "deny"): "DENY",
    ("EXECUTE", "ok"): "OBSERVE",
    ("EXECUTE", "fail"): "RETRY",
    ("RETRY", "ok"): "EXECUTE",
    ("OBSERVE", "ok"): "RETURN",
}


def step(state, event, ctx):
    if state == "EXECUTE" and event == "fail":
        if ctx["attempts"] >= ctx["max_retry"]:
            return "FAIL"
        ctx["attempts"] += 1
        return "RETRY"
    nxt = TRANSITIONS.get((state, event))
    if nxt is None:
        raise ValueError(f"illegal {state}+{event}")
    return nxt
```

每次状态转移都记一条事件，带 call_id、tool、参数哈希、授权决定和 side_effect，回放、审计、评估和恢复都靠它，见 `swe-trace-replay`、`agent-skill-eval`。

## 哪些东西必须落到外部存储

要持久化的是 tool-call ID（幂等用）、attempt、是否已执行成功、权限快照、预算 / 超时、用户确认凭证。这些要是只出现在 assistant 文本里，下一轮模型可能把转账重放一次，或者忘了刚才已经 DENY。写库、支付、发邮件这类有副作用的工具，在 EXECUTE 之前先生成 idempotency key，失败了走 STATUS_CHECK，别盲目重试。模型可以提议「再试一次」，harness 有权拒绝。Prompt injection 最多影响 PARSE 之后的语义，绕不过 AUTHORIZE，见 `agent-prompt-injection`。权限模型见 `agent-tool-permissions`；字段和类型规范（schema）见 `agent-schema-contract`。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

除了正常转移，还要检查重试计数的副作用。max_retry=1 时第一次失败进入 RETRY，第二次失败必须进入 FAIL。

```python
ctx = {"attempts": 0, "max_retry": 1}
assert step("PARSE", "ok", ctx) == "VALIDATE"
assert step("AUTHORIZE", "deny", ctx) == "DENY"
assert step("EXECUTE", "fail", ctx) == "RETRY"
assert ctx["attempts"] == 1
assert step("EXECUTE", "fail", ctx) == "FAIL"
try:
    step("PARSE", "deny", ctx)
except ValueError:
    pass
else:
    raise AssertionError("illegal transition must fail")
print("simple tests passed")
```

## 追问

**为什么不让模型直接输出 next_state？**
因为模型可能谎报已经授权。状态转移由进程里的函数执行，模型生成的文字决定不了。

**REPAIR 和 RETRY 差在哪？**
REPAIR 是改参数，工具还没执行；RETRY 是已经失败过，可能有部分副作用，所以必须幂等。

**多个工具并行调用怎么办？**
每个 call 一个独立的状态机，共享预算和权限快照。别用一个 JSON 数组配一个 attempt 计数。

**对话压缩之后怎么办？**
状态本来就存在外部存储里，需要时再把 observation 提供给模型。靠「摘要里提过已经执行」是靠不住的。

**和 ReAct 的文本轨迹是什么关系？**
ReAct 轨迹是给模型看的，这里的状态是给运行时看的。两边 id 对齐，但谁也替代不了谁。
