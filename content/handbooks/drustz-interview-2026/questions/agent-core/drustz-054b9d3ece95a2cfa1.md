---
id: drustz-054b9d3ece95a2cfa1
section: agent-core
order: 61
level: A
title: MCP (Model Context Protocol) · 自学资料
quick: 作者文档章节 · MCP (Model Context Protocol) · 自学资料
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
## 自学资料

按优先级排；spec 三页是面试当天必读，SDK repo 用来对着敲，安全两篇建立威胁直觉。

1. [MCP Spec — Lifecycle（2025-11-25）](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle) — initialize 握手 / capability negotiation / version 协商的逐条 MUST 与完整 JSON 示例，面试问"连接生命周期"就照这答 · 12 min
2. [MCP Spec — Transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports) — stdio framing 与 Streamable HTTP 的 session/SSE/续传全规则，本主题最硬的一页 · 15 min
3. [MCP Spec — Server / Tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) — tools/list、tools/call、structuredContent/outputSchema、protocol error vs `isError` 的权威定义 · 12 min
4. [MCP Spec — Security Best Practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) — confused deputy / token passthrough / session hijack / SSRF 逐个带攻击图与 MUST 级 mitigation · 18 min
5. [python-sdk（modelcontextprotocol）](https://github.com/modelcontextprotocol/python-sdk) — FastMCP 装饰器 server、Inspector 调试、transport 切换，对着 README 敲一遍 · 20 min
6. [typescript-sdk（modelcontextprotocol）](https://github.com/modelcontextprotocol/typescript-sdk) — McpServer + Zod schema + Streamable HTTP transport 的另一半参考实现 · 15 min
7. [Invariant Labs — MCP Tool Poisoning Attacks](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks) — tool poisoning + rug pull 原始披露，含对 Claude Desktop/Cursor 的 SSH key 外泄 PoC · 12 min
8. [Simon Willison — The lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) — "私有数据 + 不可信内容 + 出口通道"框架，回答 MCP 安全题的收尾金句来源 · 8 min
9. [Official MCP Registry（repo）](https://github.com/modelcontextprotocol/registry) — reverse-DNS 命名 + GitHub namespace 认证的 server 发现层，看它如何做供应链溯源 · 10 min
10. [invariantlabs-ai/mcp-injection-experiments](https://github.com/invariantlabs-ai/mcp-injection-experiments) — 可复现 tool poisoning / rug pull 的代码片段，想动手验证攻击面看这个 · 15 min

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/mcp.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/mcp.md)。作者整理资料；许可和第三方来源范围见阅读指南。
