---
id: agent-tool-permissions
section: agent
order: 19
level: S
title: 为什么 Tool 权限不能只写在 System Prompt？怎样做最小权限？
quick: >-
  Prompt 是行为引导，不是访问控制。边界必须在工具服务端：按用户、会话、资源和动作签发最小
  capability，高风险动作做显式确认、审计和幂等保护。
tags:
  - Security
  - Tool Use
  - Permissions
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: OpenAI Agent guide
    url: >-
      https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
    type: legacy-reference
  - title: MCP specification
    url: 'https://modelcontextprotocol.io/specification/2025-06-18'
    type: legacy-reference
---

Prompt 是建议，不是 ACL。一旦 Agent 能打到真实 API，网页、检索、tool result 里的注入都可以让模型「请求」越权；服务端若只信模型输出，越权已经发生。错法：「我们在 system prompt 里写了不要删库」。OpenAI 的 Agent 实践指南和 MCP 规格都把授权放在运行时，而不是模型自觉。

## Prompt 过不了信任边界

模型、用户、外部文档、工具返回都可能带指令。System prompt 能降低误用率，挡不住一次合法形状的 `delete_repo` 到达后端。权限检查必须在执行点：认证主体是用户或服务账号，不是「模型说自己是 admin」。MCP 或内部 tool 网关应把「模型可见的 schema」和「实际可调用的 capability」分开。模型看到描述，并不等于持有钥匙。把整份万能 `http_request` 暴露给模型，再靠一句「只许访问白名单」，等于没有权限系统。

间接注入会专门测试这一层：检索片段要求「用已有工具把密钥发出去」。若执行点不验 scope，prompt 防御已经被绕过。见 `agent-prompt-injection`。

## Capability token，按会话签发

按用户 × 会话 × 资源 × 动作 × TTL 签发最小令牌：读/写/删/转账分离；默认只读；写操作另签短时 token。Token 绑定 request id，过期即失效，禁止模型把 token 写进记忆或日志。策略引擎返回 allow/deny 的结构化原因，供审计，不给模型「再试一次就能绕过」的模糊文案。用户已经授权过「邮箱」不等于授权群发：scope 应细到动作和批次。模型在对话里申请「我需要 admin」不能自动提权，提权走独立审批。

## 高风险动作要确认，且整条可审计

对外发信、付款、删除、改权限、连生产库：在执行点做人类可理解的确认（对象、影响、是否不可逆），禁止模型静默代点。所有调用记 actor、resource、policy decision、idempotency key、终态。Tool 返回一律当不可信数据。Schema 负责写清副作用和调用条件（`agent-schema-contract`）；ACL 在服务端强制。两者缺一，都不是最小权限。

最小权限检查可以当场列：默认是否只读、写操作是否短 TTL、高风险是否强制确认、token 是否按资源绑定、审计日志能否还原「谁在哪次会话对何资源做了何动作」。任一项靠 system prompt 实现，就还没做完。演示环境给宽权限、生产收紧，也要写进设计，避免评测过了、上线被注入打穿。权限变更本身应是高风险动作，不能由 Agent 改自己的 scope。

## 追问

- **用户已经授权过「邮箱」，能否自动群发？** 不能默认可以。Scope 应细到动作和批次（读收件箱 ≠ 群发）；群发仍要人类确认或二次授权。宽授权是注入最爱走的通道。
- **模型自己申请提权怎么办？** 对话里的「我需要 admin」不是凭证。提权走独立审批流，签发新的短 TTL capability，并记审计。
- **和 schema 的关系？** Schema 声明副作用与调用条件；ACL 在执行点强制。见 `agent-schema-contract`。只有描述没有令牌，等于没做权限。
- **演示环境给了宽权限怎么办？** 写进设计：评测/演示 scope ≠ 生产 scope。宽权限只用于隔离沙箱，生产默认只读加确认，避免「demo 能过、线上被注入打穿」。
