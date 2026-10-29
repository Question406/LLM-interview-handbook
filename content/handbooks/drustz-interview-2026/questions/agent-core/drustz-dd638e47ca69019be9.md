---
id: drustz-dd638e47ca69019be9
section: agent-core
order: 57
level: A
title: MCP (Model Context Protocol) · 核心概念 ⭐⭐⭐
quick: 作者文档章节 · MCP (Model Context Protocol) · 核心概念 ⭐⭐⭐
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
## 核心概念 ⭐⭐⭐

| 概念 | 一句话 | 面试要点 |
|---|---|---|
| Host | LLM 应用本体（Claude Desktop / Claude Code / IDE） | 拥有 consent UI 和权限决策；一个 host 组合多个 client |
| Client | host 内的连接器，与 server 严格 1:1 | 维护 stateful session + capability negotiation |
| Server | 能力提供方（GitHub / Linear / 自建） | 一次实现、所有 host 复用——这是 MCP 的全部卖点 |
| Tools | server→model：可执行函数，JSON Schema 定义（model-controlled） | 等价于 tool registry entry + 远程 executor |
| Resources | server→app：URI 寻址的上下文数据（app-controlled） | "tools 之外还有什么"的标准答案 |
| Prompts | server→user：模板化消息/工作流（user-controlled） | slash command 的standardization形态 |
| Client 侧原语 | sampling / roots / elicitation | server 反向请求：借 host 调 LLM、问文件边界、向用户要输入 |
| stdio transport | host 拉起 server 子进程，stdin/stdout 传 JSON-RPC | 日志走 stderr；零网络暴露，本地工具首选 |
| Streamable HTTP | 单 endpoint：POST 发消息，响应可升级为 SSE 流 | 2025-03 取代旧 HTTP+SSE 双端点；`Mcp-Session-Id` 维持会话 |
| Spec 版本 | 当前 stable **2025-11-25**（date-based versioning） | 2026-07-28 RC 已公布；新增 experimental tasks、icons、OIDC discovery |





**2025-11-25 变更点 + Anthropic 生态对接（面 Anthropic 相关岗必看）**



- **2025-11-25 changelog**：experimental **tasks**（长任务可轮询/延迟取结果，对 agent 异步化关键）；tools/resources/prompts 支持 **icons** 元数据；auth 增强——OIDC Discovery、OAuth **Client ID Metadata Documents**（替代裸 DCR）、`WWW-Authenticate` 增量 scope consent；tool name 规范化单一格式；stdio 明确 stderr 可打任意日志。
- **版本史**：2024-11-05（首版，HTTP+SSE）→ 2025-03-26（Streamable HTTP、OAuth 2.1）→ 2025-06-18（elicitation、structured tool output、resource indicators）→ 2025-11-25（stable）。
- **Anthropic Messages API 的 MCP connector**（beta `mcp-client-2025-11-20`）：`mcp_servers=[{type:"url", url, name}]` 必须配对 `tools=[{type:"mcp_toolset", mcp_server_name}]`，缺一个 400——Anthropic 服务端替你连 server，你不跑 client。
- **Managed Agents**：agent 上声明 `mcp_servers`（只有 type/name/url，无 auth），凭据放 **vault**，按 server URL 匹配、OAuth 自动 refresh；session 经 `vault_ids` 挂载。凭据从不进 sandbox——egress 侧注入，这是对 token 泄漏的架构级防御。
- **Claude Code / Desktop** 是典型 host：`.mcp.json` 配 stdio/HTTP server；Python SDK 有 `anthropic.lib.tools.mcp` 把 MCP tool 转成 tool runner 可用的本地 tool。
- 采用面：OpenAI、Google DeepMind 2025 年先后采用 MCP，事实上的行业标准。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/mcp.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/mcp.md)。作者整理资料；许可和第三方来源范围见阅读指南。
