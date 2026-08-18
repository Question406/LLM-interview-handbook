---
id: agent-tool-permissions
section: agent
order: 19
level: S
title: 为什么 Tool 权限不能只写在 System Prompt？怎样做最小权限？
quick: >-
  Prompt 是行为引导，不是访问控制。真正的边界必须在工具服务端：按用户、会话、资源和动作签发最小
  capability，并把高风险动作做显式确认、审计和幂等保护。
tags:
  - Security
  - Tool Use
  - Permissions
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: OpenAI Agent guide
    url: >-
      https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
    type: legacy-reference
  - title: MCP specification
    url: 'https://modelcontextprotocol.io/specification/2025-06-18'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>一旦 Agent 能读写外部系统，模型、网页内容、检索结果和 tool result 都可能带来不可信指令。System prompt 可以降低误用率，却无法阻止越权请求到达 API。</p><ul><li><b>最小 capability：</b>令牌只允许当前用户、当前资源、当前动作和短 TTL；读、写、删除、转账等权限分离。</li><li><b>强制确认：</b>对外发信、删除、权限变更等高影响动作，在执行点要求可理解的确认，不让模型替用户静默决定。</li><li><b>可审计执行：</b>保存结构化 actor、resource、policy decision、request id 和最终状态；所有返回内容都按不可信数据处理。</li></ul><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/" target="_blank" rel="noreferrer">OpenAI Agent guide</a><a href="https://modelcontextprotocol.io/specification/2025-06-18" target="_blank" rel="noreferrer">MCP specification</a></div></div>
