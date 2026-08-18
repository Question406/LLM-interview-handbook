---
id: mcp-sampling-loop-boundaries
section: mcp-security
order: 3
level: A
title: MCP Server 嵌套 Sampling + Tool loop 时，如何阻止服务器借客户端模型、上下文和工具扩大权限或无限递归？
quick: 把 server 发起的 sampling 当作受限 capability：用户可见并可拒绝 prompt，context 和工具按最小集合传递；每轮设置调用、token、费用与深度上限，严格关联 request/response，并为外部副作用单独确认。
tags:
  - MCP
  - Sampling
  - Agent Loop
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: MCP Sampling
    url: https://modelcontextprotocol.io/specification/2025-11-25/client/sampling
    type: primary
---

server 请求 client sampling 时，不应自动获得 client 的全部模型、memory、tool 和用户身份。host 应显示/记录请求来源和 prompt，裁剪 context，指定可用工具和输出上限；敏感数据或高风险工具必须再次走用户确认。

为每个根请求设置最大 recursion depth、tool call 数、token/费用、墙钟时间和并发数。每一轮将 sampling request、model response、tool call、tool result 以 request ID 串联，防止 server 注入无关结果或制造不可归因循环。

超过预算时安全终止并保存 trace。没有预算控制的“自主 loop”既是成本问题，也是 server 利用 client capability 的权限升级路径。
