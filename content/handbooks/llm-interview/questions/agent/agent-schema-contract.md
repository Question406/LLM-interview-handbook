---
id: agent-schema-contract
section: agent
order: 18
level: S
title: 一个可供 Agent 稳定调用的 Tool Schema，除了参数类型还必须写什么？
quick: >-
  Tool schema 是执行契约，不只是 JSON
  字段。至少应明确何时调用、必填约束、单位/枚举、权限和副作用、幂等语义、可恢复错误与结构化返回；服务端必须验证，不能只相信模型输出。
tags:
  - Tool Use
  - Schema
  - Agent
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: Tool-use schema guide
    url: >-
      https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use
    type: legacy-reference
  - title: MCP specification
    url: 'https://modelcontextprotocol.io/specification/2025-06-18'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>模型会把 tool description 当作行动空间的一部分。一个只写了字段类型的 schema，往往会导致“JSON 合法但业务错误”的调用。</p><ul><li><b>输入：</b>字段含义、单位、枚举、默认值、互斥/依赖约束，以及哪些信息禁止模型自行猜测。</li><li><b>执行：</b>read/write 副作用、权限范围、是否可重试、idempotency key 和异步任务状态。</li><li><b>输出：</b>machine-readable success/error code、可呈现摘要、下一步可行动信息，而非让模型解析一大段模糊 prose。</li></ul><p>服务端应做 schema 与业务规则验证；让 LLM 自己“遵守格式”只是一层 UX 辅助，不是安全边界。</p><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use" target="_blank" rel="noreferrer">Tool-use schema guide</a><a href="https://modelcontextprotocol.io/specification/2025-06-18" target="_blank" rel="noreferrer">MCP specification</a></div></div>
