---
id: agent-schema-contract
section: agent
order: 18
level: S
title: 一个可供 Agent 稳定调用的 Tool Schema，除了参数类型还必须写什么？
quick: "除了参数类型，Tool Schema 还要写清什么时候调、什么时候别调，必填和依赖约束、单位和枚举、权限和副作用、幂等性、机器可读的错误码和返回格式。描述是写给模型看的，这些要求最后都由服务端校验，不能信模型的输出。"
tags:
  - Tool Use
  - Schema
  - Agent
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: Tool-use schema guide
    url: >-
      https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use
    type: legacy-reference
  - title: MCP specification
    url: 'https://modelcontextprotocol.io/specification/2025-06-18'
    type: legacy-reference
---

除了参数类型，Schema 还要写清何时调用、何时不要调、单位和枚举、权限和副作用、幂等性、可恢复的错误码和返回格式。它是一份执行契约，描述写给模型看，校验放在服务端做。

只写 JSON 类型，得到的是「格式合法、业务错误」的调用：单位错、副作用不明、超时后盲目重放。比如转账工具的 `amount` 只标了 number，模型以为单位是元，后端按分处理；请求超时后模型又发一次，钱就转了两笔。constrained decoding 或者「模型会守格式」只管得了格式，管不了正确性。Anthropic 的工具调用文档和 MCP 规格都强调同一件事：描述给模型看，校验在服务端做。

## 调用条件、单位、禁止猜测

先写调用条件。Description 写何时调用、何时不要调：缺用户确认、缺幂等键、目标不在授权范围时都别调。When-not-to-call 写清楚，router 才有负类可学，见 `agent-tool-routing`。必填、互斥、依赖（有 `end` 就必须有 `start`）写进字段和类型规范（schema）。单位和枚举明确固定：金额是分还是元、时区、货币 ISO 码；邮箱、账号、资源 id 禁止模型「合理推测」。有副作用的默认值必须显式写出来。别把整份内部 OpenAPI 塞进 context，只暴露当前会话允许的工具和精简字段，选错率和注入面都会降。模型可见的枚举也可以比后端能力小，防止探索式滥用，比如「先试试 admin 接口」。

再写副作用和错误。每个工具标明是 read 还是 write、会不会产生外部副作用、权限范围、能不能重试。写操作提供 `idempotency_key` / 事务 id，并说明超时以后该去查状态，别再发一封邮件，见 `arl-retry`。输出要结构化：`ok`、机器可读的 `error_code`（`INVALID_ARGUMENT`、`PERMISSION_DENIED`、`CONFLICT`、`UNKNOWN_SIDE_EFFECT`）、给人看的摘要、下一步字段（`status_url`、`retryable`）。别只返回一段文字，让模型再用正则去抠信息。异步工具要约定轮询方式和终态，免得把「已接受」当成「已完成」。

## 边界在服务端验证

模型按格式输出只是改善了使用体验。服务端要做 schema、业务规则和权限三层校验，类型对但越权、单位错、重复提交的，一律拒绝并返回结构化错误。契约测试要走真实的错误码和副作用路径，光测 happy-path JSON 不够。权限题（`agent-tool-permissions`）管能不能调，这题管调的时候契约全不全，两边都有，Agent 才稳。

评审一张 schema 时我会按这个顺序过：when-to-call / when-not-to-call、单位与枚举、副作用级别、幂等键、超时后去查谁、错误码是不是机器可读、服务端会不会拒绝「类型对但业务错」。缺一项，就别让 Agent 碰生产写接口。把 schema 当成一个 API 产品来维护，别把它当输入提示（prompt）的附件。

## 追问

**要不要把整份 OpenAPI 塞进 context？**
不要。只暴露当前会话允许的工具和精简字段，选错和注入面都会少。内部管理接口根本不该出现在模型可见的 schema 里。

**报错了，该重试还是改参数？**
看 `error_code` 和 `retryable`：参数错就改参，权限错就停，未知副作用先查状态。别让模型从一段散文里猜。

**和权限题怎么分工？**
Schema 声明副作用和调用条件，ACL 在运行时强制执行，见 `agent-tool-permissions`。契约写得再完整，服务端不校验，照样会被「合法 JSON」打穿。

**契约要改字段语义怎么办？**
做版本化。旧轨迹里的旧字段不能悄悄改了语义，否则离线数据和线上工具的含义就对不上了。
