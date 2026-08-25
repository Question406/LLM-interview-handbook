---
id: agent-mcp
section: agent
order: 5
level: S
title: MCP、Function Calling、Agent Framework 有什么区别？
quick: >-
  Function calling 讲的是模型怎么吐结构化调用。MCP 是 host/client/server 之间，标准化发现和交换
  tools、resources、prompts 这些能力和上下文的协议。Agent framework 管的是
  loop、planning、memory、recovery 这类上层 orchestration。
tags:
  - MCP
  - Tool
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources:
  - title: ↗ MCP 官方
    url: 'https://modelcontextprotocol.io/'
    type: legacy-reference
  - title: ↗ MCP Specification
    url: 'https://modelcontextprotocol.io/specification/'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Function calling 讲的是模型怎么吐结构化调用。MCP 是 host/client/server 之间，标准化发现和交换 tools、resources、prompts 这些能力和上下文的协议。Agent framework 管的是 loop、planning、memory、recovery 这类上层 orchestration。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><div class="table-wrap"><table><thead><tr><th>概念</th><th>解决的问题</th><th>不负责什么</th></tr></thead><tbody><tr><td>Function calling</td><td>模型如何表达“调用哪个函数、参数是什么”</td><td>外部服务发现、完整 Agent loop</td></tr><tr><td>MCP</td><td>应用如何标准化连接外部 capability/context provider</td><td>不定义 planning/memory/retry 策略</td></tr><tr><td>Agent framework/harness</td><td>如何组织 state→model→tool→observation 的运行循环</td><td>协议本身可由 MCP/OpenAPI/自定义接口实现</td></tr></tbody></table></div><p>所以把 MCP 说成「统一 Tool API」不够准。MCP server 可以暴露 tools、resources、prompts 这些 primitives；host 仍然决定怎么把它们塞进 agent context 和控制流。</p><p>安全上，MCP server 是外部 trust boundary：description 和 resource 可能带 prompt injection，tool 可能有 side effects。permission 和 schema enforcement 必须由 host 自己做。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>MCP server 能做哪些攻击？</summary><div class="follow-answer"><p>恶意 tool description 注入、resource 上的 prompt injection、诱导把 secret 带出去、提供带危险 side-effect 的 tool、返回被污染的 observation。</p></div></details><details class="followup"><summary>MCP 与 OpenAPI 是同一层吗？</summary><div class="follow-answer"><p>有重叠，但不是同一层。OpenAPI 描述 HTTP API；MCP 定义面向 AI host 的 capability/context 协议和交互语义，底层照样可以调任意 API。</p></div></details></div>
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://modelcontextprotocol.io/" target="_blank" rel="noopener noreferrer">↗ MCP 官方</a><a href="https://modelcontextprotocol.io/specification/" target="_blank" rel="noopener noreferrer">↗ MCP Specification</a></div>
