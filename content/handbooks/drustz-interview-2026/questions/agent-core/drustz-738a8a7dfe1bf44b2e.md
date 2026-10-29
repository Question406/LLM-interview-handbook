---
id: drustz-738a8a7dfe1bf44b2e
section: agent-core
order: 56
level: A
title: MCP (Model Context Protocol) · 30 秒版本（3 句话）⭐⭐⭐
quick: 作者文档章节 · MCP (Model Context Protocol) · 30 秒版本（3 句话）⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/mcp.md
    type: primary
---
## 30 秒版本（3 句话）⭐⭐⭐

1. MCP 是 Anthropic 2024-11 发起的开放协议，用 JSON-RPC 2.0 把 "LLM 应用 ↔ 外部能力" 从 N×M 集成变成 N+M：host（应用）内嵌 client，与 server 1:1 连接，initialize 时做 capability negotiation。
2. Server 暴露三类原语——tools（给模型执行）、resources（给应用取上下文）、prompts（给用户选模板）；client 也反向提供 sampling / roots / elicitation，server 可借 host 的模型和用户交互。
3. 对手写 tool loop 的人：MCP 只是 tool registry 的standardization发现 + 传输层，executor 的验证、权限、预算责任一点没变——第三方 server 的输出仍是 untrusted tool output。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/mcp.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/mcp.md)。作者整理资料；许可和第三方来源范围见阅读指南。
