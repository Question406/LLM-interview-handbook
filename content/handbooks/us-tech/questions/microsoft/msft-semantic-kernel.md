---
id: msft-semantic-kernel
section: microsoft
order: 9
level: A
title: Microsoft：Agent / Semantic Kernel 插件边界，工具失败怎么收
quick: "Semantic Kernel 插件要明确能力、当前用户身份与副作用，原生函数负责系统调用，语义函数负责文本生成。工具失败返回可行动的结构化状态，运行时限制重试与超时，写操作先确认或保证幂等；用户看到的完成状态以系统结果为准。"
tags:
  - Microsoft
  - Semantic Kernel
  - Agent
  - Tools
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Semantic Kernel overview
    url: https://learn.microsoft.com/en-us/semantic-kernel/overview/
    type: primary
  - title: Semantic Kernel filters
    url: https://learn.microsoft.com/en-us/semantic-kernel/concepts/enterprise-readiness/filters
    type: primary
---

Semantic Kernel 接工具时，我会先定义每个函数能做什么、以谁的身份执行，以及失败后如何处理。比如日历 API 超时，模型不能继续说「已经约上了」；它需要收到明确错误，再决定告知用户或调整计划。

公开文档把 plugin 作为技能包、filter 作为中间件，后来的 Agent Framework 也需要这些边界。与 `msft-copilot-ground` 一样，ACL 由系统执行。

## 暴露最小能力，并约束执行

原生函数是 C# / Python 代码，可查日历、发邮件、改工单、跑 SQL，有 ACL 且可能产生副作用；语义函数是带提示的 LLM 调用，适合摘要改写，不应自行带副作用。

每轮只向模型暴露当前任务需要的 schema，避免搜索文档时同时自动开放删除订阅或转账。原生函数使用当前用户 token 调 Graph，密钥、连接字符串和 PAT 留在代码里，模型只提供业务 id。只读可自动调用，写、发、删先确认或二次校验，filter 可在 invocation 前检查参数。

Planner / 自动 function calling 的循环设最大轮数和每轮超时，避免在 429 或超时上不停重试，见 `msft-azure-tpm`。

## 错误分别给模型、运行时和用户

模型收到简短的结构化错误，例如 `{ "status": "error", "code": "timeout", "retryable": true, "hint": "calendar busy, try later" }`，而非堆栈。权限拒绝、资源不存在等用 `retryable=false` 禁止重复同样调用。

运行时在 `IFunctionInvocationFilter` / auto-invocation filter 中 `try/catch`，记录日志指标，必要时改 `FunctionResult`。只读超时可有限退避，写操作默认不重试，除非有 idempotency key，避免创建两张工单。

对用户，副作用前展示「即将给 Alice 发邮件，主题是……」并确认。失败时明确说明执行失败，不能猜测成功；超时后应以实际系统记录核实是否发出。

```python
async def guarded_call(fn, args, *, mutating: bool, retries: int = 1):
    if mutating:
        return {"status": "need_confirm", "fn": fn.__name__, "args": args}
    last = None
    for _ in range(retries + 1):
        try:
            return {"status": "ok", "data": await fn(**args)}
        except TimeoutError as e:
            last = str(e)
    return {"status": "error", "retryable": True, "error": last}
```

这段骨架表达的是边界：写操作先返回 need_confirm，只读失败有有限次数，结果结构化。评测看工具成功率、误调率、重复副作用，以及失败后的幻觉率，不能把口头完成当任务完成。

## 追问

**HTTP 200，业务却失败怎么办？**
原生函数把邮箱满了等业务失败映射成结构化 error，不让模型自己从 HTML 猜状态。

**多工具可以并行吗？**
独立只读可并行，有依赖或写操作串行，按资源 id 加锁，避免两次修改同一事件。

**与 Copilot plugin / Graph connector 怎么衔接？**
分发通道虽不同，身份和 ACL 继续沿调用传递，不能另开管理员旁路。

**模型一直重试怎么办？**
Filter 记录失败次数，达到上限短路为 `retryable=false`，将控制权交还用户。
