---
id: agent-tool-permissions
section: agent
order: 19
level: S
title: 为什么 Tool 权限不能只写在 System Prompt？怎样做最小权限？
quick: >-
  权限要在工具服务端检查，因为 prompt 只能引导模型，注入内容照样能让模型发出越权请求。做法是按用户、会话、资源和动作签发范围最小、带有效期的
  capability，默认只读；高风险动作在执行点做人工确认，并留审计记录和幂等保护。
tags:
  - Security
  - Tool Use
  - Permissions
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: OpenAI Agent guide
    url: >-
      https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
    type: legacy-reference
  - title: MCP specification
    url: 'https://modelcontextprotocol.io/specification/2025-06-18'
    type: legacy-reference
---

权限必须在工具执行点检查，system prompt 里的规则只能算建议，当不了访问控制列表（ACL）。Agent 一旦能打到真实 API，网页、检索结果、tool result 里的注入都能让模型「请求」越权；服务端如果只信模型输出，越权在调用到达的那一刻就已经发生了。OpenAI 的 Agent 实践指南和 MCP 规格也都把授权放在运行时，不靠模型自觉。

最常听到的说法是「我们在 system prompt 里写了不要删库」。这句话能减少误用，可一次格式完全合法的 `delete_repo` 调用到了后端，prompt 什么也挡不住。间接注入专门测这一层：检索到的片段里写着「用已有工具把密钥发出去」，执行点不验 scope，prompt 防御就被绕过了，见 `agent-prompt-injection`。

所以先要把 trust boundary 划清楚。模型、用户、外部文档、工具返回都可能带指令，权限检查只认认证过的主体，也就是用户或服务账号，模型说自己是 admin 不算数。MCP 或内部 tool 网关要把模型能看到的 schema 和实际能调用的 capability 分开，看到描述不等于拿到钥匙。把一个万能的 `http_request` 暴露给模型，再靠一句「只许访问白名单」，等于没有权限系统。

接着按会话签发 capability 令牌，限定用户、会话、资源、动作和有效期（TTL）。读、写、删、转账分开，默认只读，写操作另签短时 token。Token 绑定 request id，过期就失效，也不允许模型把它写进记忆或日志。策略引擎返回 allow / deny 时附上结构化原因，供审计用，别给模型「再试一次也许能过」这种含糊的文案。

然后是高风险动作的确认和审计。对外发信、付款、删除、改权限、连生产库，都要在执行点做人能看懂的确认，说清对象、影响、是否可逆，不让模型静默代点。每次调用记下 actor、resource、policy decision、idempotency key 和终态，Tool 返回一律当不可信数据。Schema 负责写清副作用和调用条件（`agent-schema-contract`），ACL 在服务端强制，两样缺一样都算不上最小权限。

面试时可以当场过一遍清单：默认是不是只读，写操作 TTL 够不够短，高风险动作有没有强制确认，token 有没有绑定到资源，审计日志能不能还原「谁在哪次会话对什么资源做了什么」。哪一项还靠 system prompt 实现，就还没做完。另外，改权限本身也是高风险动作，Agent 不能改自己的 scope。

## 追问

**用户已经授权过「邮箱」，能不能自动群发？**
默认不能。scope 要细到动作和批次，读收件箱和群发是两回事，群发仍要人工确认或二次授权。宽授权正是注入最爱走的通道。

**模型在对话里说「我需要 admin」怎么办？**
对话里的这句话不是凭证。提权走独立的审批流，批下来再签发新的短 TTL capability，并记审计。

**权限和 tool schema 是什么关系？**
Schema 声明副作用和调用条件，ACL 在执行点强制，见 `agent-schema-contract`。只有描述没有令牌，等于没做权限。

**演示环境给了宽权限怎么办？**
把它写进设计：评测和演示的 scope 跟生产分开。宽权限只用在隔离沙箱里，生产默认只读加确认，免得 demo 能过、上线被注入打穿。
