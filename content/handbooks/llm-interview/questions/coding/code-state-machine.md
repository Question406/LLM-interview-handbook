---
id: code-state-machine
section: coding
order: 9
level: A
title: 设计 Tool-Call State Machine：哪些状态不能交给 LLM 自己“记”？
quick: >-
  建议显式 runtime 状态
  PARSE→VALIDATE→AUTHORIZE→EXECUTE→OBSERVE→RETRY/FAIL→RETURN，并持久化
  attempt、tool-call ID、权限、side-effect status。安全/幂等状态不应只存在自然语言 context 中。
tags:
  - Agent
  - State Machine
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: OpenAI — A practical guide to building AI agents
    url: https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
    type: reference
  - title: MCP specification
    url: https://modelcontextprotocol.io/specification/2025-06-18
    type: reference
---

错法：把 tool 调用的进度写进对话里让模型「自己记得」。LLM 擅长语义决策（叫不叫、填哪个槽），但 transaction、权限、重试次数、是否已有副作用必须由 harness 结构化保存。压缩 context、幻觉、进程重启都会丢掉自然语言里的安全信息。权限模型见 `agent-tool-permissions`；schema 见 `agent-schema-contract`。
## 显式状态：PARSE 到 RETURN，失败有单独边

建议主路径：

```text
PARSE -> VALIDATE -> AUTHORIZE -> EXECUTE -> OBSERVE -> RETURN
              |             |            |
            REPAIR        DENY       RETRY / UNKNOWN
                                      |
                                    STATUS_CHECK
```

PARSE 把模型输出变成结构化 call（名字、参数、id）；VALIDATE 对 JSON schema；AUTHORIZE 查策略（只读、是否允许写、是否要人审）；EXECUTE 真正打工具；OBSERVE 把结果变成 machine-readable observation；RETURN 交回模型或用户。REPAIR 只修参数，不跳过授权。DENY 不执行。RETRY 受 `attempt` 上限约束。UNKNOWN / STATUS_CHECK 用于超时后查幂等键，而不是再发一次付款。

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

每个 transition 写一条 event（call_id、tool、args hash、auth decision、side_effect）。供 replay、audit、eval、checkpoint。见 `swe-trace-replay`、`agent-skill-eval`。

## 什么不能只存在 context 里

必须持久化：tool-call ID（幂等）、attempt、是否已执行成功、权限快照、预算 / 超时、用户确认 token。这些若只出现在 assistant 文本里，下轮模型可能重放一次转账，或忘掉已经 DENY。副作用工具（写库、支付、发邮件）在 EXECUTE 前生成 idempotency key，失败走 STATUS_CHECK 而不是盲目重试。LLM 可以提议「再试一次」，harness 有权拒绝。Prompt injection 只能影响 PARSE 之后的语义，不能绕过 AUTHORIZE，见 `agent-prompt-injection`。

## 追问

- **为什么不让模型输出 next_state？** 模型可谎报已授权。状态转移函数在进程内，不在 token 里。
- **REPAIR 和 RETRY 差在哪？** REPAIR 改参数、未执行；RETRY 已失败过，可能已有部分副作用，必须幂等。
- **多工具并行？** 每个 call 独立状态机，共享预算与权限快照。不要一个 JSON 数组混一个 attempt 计数。
- **压缩对话后怎么办？** 状态在外部 store，observation 按需注入。不能靠「摘要里提过已经执行」。
- **和 ReAct 文本轨迹？** ReAct 是给模型看的；本机状态是给运行时看的。两者 id 对齐，但不互相替代。

