---
id: agent-schema-contract
section: agent
order: 18
level: S
title: 一个可供 Agent 稳定调用的 Tool Schema，除了参数类型还必须写什么？
quick: "Tool Schema 要说明工具怎么调用、在什么条件下可以调用。除了参数类型，还应写清必填约束、单位和枚举、权限、副作用、幂等性、可恢复的错误以及返回格式。服务端必须验证这些要求，不能只信模型输出。"
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

只写 JSON 类型会得到「合法但业务错误」的调用：单位错、副作用不明、超时后盲目重放。Schema 是执行契约，不是字段清单。常见误区是：把 constrained decoding 或「模型会守格式」当成正确性。Anthropic 的 工具调用 文档和 MCP 规格都强调：描述给模型看，校验在服务端做。

## When-to-call、单位、禁止猜测

Description 要写何时调用与何时不要调：缺用户确认、缺幂等键、目标不在授权范围时不要调。必填、互斥、依赖（有 `end` 必须有 `start`）写进 字段和类型规范（schema）。单位与枚举明确固定下来：金额是分还是元、时区、货币 ISO 码；禁止模型「合理推测」邮箱、账号、资源 id。默认值若有副作用必须显式。不要把整份内部 OpenAPI 塞进 context：只暴露当前会话允许的工具和精简字段，既降选错率也减注入面。

模型可见的枚举可以小于后端能力，防止探索式滥用（「先试试 admin 接口」）。When-not-to-call 写清楚，router 才有负类可学，见 `agent-tool-routing`。

## 副作用、幂等、结构化错误

每个工具标明 read vs write、是否发送外部副作用、权限范围、是否可重试。写操作提供 `idempotency_key` / 事务 id，并说明超时后应查状态而不是再发一封邮件（见 `arl-retry`）。输出必须结构化：`ok`、机器可读 `error_code`（`INVALID_ARGUMENT`、`PERMISSION_DENIED`、`CONFLICT`、`UNKNOWN_SIDE_EFFECT`）、人类摘要、下一步字段（`status_url`、`retryable`）。不要只返回一段文字，让模型再用正则提取信息。异步工具约定轮询与终态，避免把「已接受」当成「已完成」。错误该重试还是改参，由 `error_code` 和 `retryable` 决定，不要让模型猜。

## 服务端验证才是边界

模型按格式输出只能改善使用体验。服务端做 schema + 业务规则 + 权限校验：类型对但越权、单位错、重复提交，一律拒绝并回结构化错误。契约测试要用真实错误码和副作用路径，而不是只测 happy-path JSON。权限题（`agent-tool-permissions`）管「能不能调」；本题管「调的时候契约是否完整」。两边一起，Agent 才稳定。

评审一张 schema 时按清单过：when-to-call / when-not-to-call、单位与枚举、副作用级别、幂等键、超时后查谁、错误码是否机器可读、服务端是否拒绝「类型对但业务错」。缺一项就不要让 Agent 碰生产写接口。契约变更要版本化：旧轨迹里的旧字段不能 silently 改语义，否则离线数据和线上工具的含义会同时改变。把 schema 当 API 产品，而不是 输入提示（prompt） 附件。

## 追问

- **要不要把整份 OpenAPI 塞进 context？** 不要。只暴露当前会话允许的工具和精简字段，降低选错与注入面。内部管理接口根本不该出现在模型可见 schema 里。
- **错误该重试还是改参？** 由 `error_code` 和 `retryable` 决定：参数错改参，权限错停，未知副作用先查状态。不要让模型从散文里猜。
- **和权限题的分工？** Schema 声明副作用与调用条件；ACL 在运行时强制。见 `agent-tool-permissions`。契约完整但服务端不验，仍会被「合法 JSON」打穿。
- **契约改字段语义怎么办？** 版本化。旧轨迹不能 silently 沿用新单位或新默认值，否则离线数据与线上工具的含义会不一致。
