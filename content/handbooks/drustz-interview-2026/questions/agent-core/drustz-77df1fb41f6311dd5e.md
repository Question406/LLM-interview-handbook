---
id: drustz-77df1fb41f6311dd5e
section: agent-core
order: 58
level: A
title: MCP (Model Context Protocol) · 面试常问 3 题 ⭐⭐⭐
quick: 作者文档章节 · MCP (Model Context Protocol) · 面试常问 3 题 ⭐⭐⭐
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
## 面试常问 3 题 ⭐⭐⭐

### Q1：什么时候用 MCP，什么时候直接函数注册？





**参考打法**



- 判断轴是"谁维护集成、被多少 host 复用"：自家 agent 调自家内部 API → in-process 函数注册，少一层 RPC/序列化/协议协商，延迟与可调试性都赢。
- 能力需要跨 host 复用（Claude Desktop + IDE + 自家产品）或由第三方维护（GitHub/Linear 官方 server）→ MCP，省掉每个 host 写一遍 adapter。
- 强调边界：MCP 不接管 executor 责任——schema 验证、permission gate、timeout/retry、token 预算仍在你的 loop 里；它只回答 "tool 实现放哪、怎么发现、怎么传输"。
- 混合是常态：Claude Code 内置工具原生注册，第三方经 MCP 挂进同一个 loop——对 model 而言都只是 tools 数组里的 entry，loop 代码不感知来源。
- 成本提醒：N 个 server 全量 `tools/list` 会吃 context 且破坏 prompt cache——生产上要 defer loading / tool search（Anthropic API 的 tool search tool 就是这个动机）。





> 高分句：MCP 是 tool registry 的standardization传输层，不改变 executor 的验证、权限、预算责任。

### Q2：讲讲 MCP 的连接生命周期和两种 transport 的取舍。





**参考打法**



- 生命周期：`initialize`（协议版本 + 双向 capability negotiation）→ `initialized` 通知 → 正常收发（request / response / notification 三种 JSON-RPC 消息）→ 关闭；**stateful** 是它和普通 REST API 的本质区别。
- stdio：host 把 server 当子进程拉起，stdin/stdout 传消息、stderr 打日志；进程边界即安全边界，本地工具（文件系统、git、本地 DB）首选。
- Streamable HTTP：单一 endpoint，client POST 发消息，server 可把响应升级成 SSE 流做 server→client 推送（notifications、sampling 请求）；`Mcp-Session-Id` 维持会话，支持 resumability/redelivery。
- 为什么废弃旧 HTTP+SSE：旧版要求一条常开的独立 SSE 长连接 + 单独 POST endpoint，对 serverless / LB 不友好；Streamable HTTP 允许无状态部署、按需升级 SSE。
- 远程 server 认证走 OAuth 2.1（PKCE + resource indicators 防 token 错发）；2025-11-25 加了 OIDC discovery 与 Client ID Metadata Documents。





> 高分句：stdio 用进程隔离换安全，Streamable HTTP 用单 endpoint + 按需 SSE 换可部署性——选型只取决于 server 跑在哪。

### Q3：接入第三方 MCP server，你的安全模型怎么设计？





**参考打法**



- 信任模型第一句：第三方 server 的一切产出——tool result、**tool description**、resource 内容——都是 untrusted input；description 会进模型上下文，是 prompt injection 载体（tool poisoning；server 还能事后改 description，即 rug pull）。
- executor 侧防线一条不少：per-tool permission policy（读自动放行、写走审批）、对 server 返回做 schema 校验、egress allowlist、全量审计日志——MCP 协议本身不替你做任何一层，spec 明说 host MUST 获得用户 consent 才能调 tool。
- **Confused deputy**：MCP proxy server 用 static client ID 代理三方 OAuth 时，三方 AS 的 consent cookie + 攻击者动态注册恶意 redirect_uri = 跳过同意页窃取授权码；spec 要求 proxy 实现 per-client consent + redirect_uri 精确匹配。
- **Token passthrough** 是 spec 明令禁止的反模式：server MUST NOT 接受不是 issue 给自己的 token 转发下游——绕过下游 rate limit/validation，且审计链断裂；正确做法是 token 按 audience 分层交换。
- 收尾用组合攻击框架（lethal trifecta）：私有数据访问 + 不可信内容 + 出口通道，三者共存才致命——砍掉任意一条边（如禁网络出口、砍写权限）比逐条过滤 injection 可靠。





> 高分句：MCP 扩大的是供应链攻击面，不是新漏洞类型——防线还是 executor 的老三样：权限门、输出不可信、出口控制。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/mcp.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/mcp.md)。作者整理资料；许可和第三方来源范围见阅读指南。
