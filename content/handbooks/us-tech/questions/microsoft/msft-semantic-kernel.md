---
id: msft-semantic-kernel
section: microsoft
order: 9
level: A
title: Microsoft：Agent / Semantic Kernel 插件边界，工具失败怎么收
quick: >-
  插件是权限和副作用边界，不是「多几个 prompt」。原生函数进系统，语义函数只产文本。失败要结构化回给模型、限制重试，写操作先确认。过滤器是中间件，不要把异常吞成一句「出错了」让模型瞎编。
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

微软应用 / Agent 岗会问 Semantic Kernel（以及后来的 Agent Framework）怎么把工具接到模型上。评委要的不是 SDK 方法名，是 **边界**：哪些函数模型能调、失败时谁看见什么、副作用会不会被重试放大。公开文档把 plugin 当技能包，filter 当中间件。设计题和 `msft-copilot-ground` 一样，权限先于聪明。

## 插件边界：能力、身份、副作用

我会把 plugin 分成两类，不要混在一个「tools」列表里：

- **原生函数。** C# / Python 代码：查日历、发邮件、改工单、跑 SQL。有真实副作用和 ACL。
- **语义函数。** 其实是带提示的 LLM 调用：摘要、改写。不该有副作用。把它当「工具」只是为了编排。

边界规则：

1. **最小暴露。** 模型只看见当前任务需要的函数 schema。把「删除订阅」「转账」和「搜索文档」放在同一轮 auto-invoke 里，是在请模型误调。
2. **身份向下传。** 函数内部用当前用户的 token 调 Graph，而不是用应用身份扫租户。这和 Copilot grounding 同一条 ACL。
3. **副作用分级。** 只读（检索）可自动调。写、发、删必须确认或二次校验。SK 的 filter 可以在 invocation 前拦参数，比把「请谨慎」写进 system prompt 硬。
4. **密钥不出提示。** 连接字符串、PAT 留在 native 代码里。模型参数只允许业务 id，不允许「把连接串当参数传进来」。

Planner / 自动 function calling 会多步调工具。要设 **最大轮数** 和 **每轮超时**。没有上限的 ReAct 循环会在 429 和超时上把自己打崩，见 `msft-azure-tpm`。

## 工具失败怎么收：别把异常变成幻觉燃料

自动调用时，函数一抛，默认可能往对话里塞一句模糊的 tool error，模型接着「猜」结果。这是最常见的产品事故：日历 API 超时，模型仍说「已经帮你约上了」。

收口分三层：

**对模型。** 返回结构化、短、可行动的错误，不要堆栈。例如 `{ "status": "error", "code": "timeout", "retryable": true, "hint": "calendar busy, try later" }`。`retryable=false`（权限拒绝、资源不存在）时明确禁止再调同一函数。模型可以改口或问用户，不能假装成功。

**对运行时。** Filter（`IFunctionInvocationFilter` / auto-invocation filter）里 `try/catch`：日志、指标、可选改写 `FunctionResult`。只读超时：有限次退避。写操作：**默认不重试**，除非函数幂等（带 idempotency key）。重试一次「创建工单」会开两张单。

**对用户。** 需要副作用时停下来确认：「即将给 Alice 发邮件，主题是……」。超时后说「没发出去」，不要说「可能发了」。状态以系统记录为准，不以模型口述为准。

伪代码表达的是合同，不是让你背 SK API：

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

评测：工具成功率、误调率（不该调却调了）、重复副作用次数、在工具失败后的幻觉率。只报「任务完成率」会把「编造成功」算成正例。

## 追问

- **工具返回 200 但业务失败？** HTTP 成功不是业务成功。原生函数要自己把「邮箱满了」映射成结构化 error，别让模型解析一段 HTML。
- **多工具并行？** 只读可并行。有依赖或写操作串行，按资源 id 加锁，避免两次改同一事件。
- **和 Copilot plugin / Graph connector？** 同一套 ACL 故事，只是分发通道不同。不要为 Agent 另开一条绕过 Graph 的管理员通道。
- **模型一直重试同一工具？** filter 记失败次数，超过就短路成 `retryable=false`，并把控制权交还用户。
