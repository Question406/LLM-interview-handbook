---
id: mcp-tool-catalog-trust
section: mcp-security
order: 2
level: S
title: MCP ToolAnnotations 能否作为执行授权依据？Tool catalog 在运行中变更时如何做 server trust、schema / description diff、pinning 和重新确认？
quick: 不能。annotations 只是 server 声称的提示，不是可信授权。host / policy / executor 必须独立判定权限；catalog 变更需身份 pinning、schema 与描述 diff、高风险变更重新确认，并保留已批准版本。
tags:
  - MCP
  - Tool Security
  - Policy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: MCP Tool Annotations
    url: https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/
    type: primary
---

`readOnly`、`destructive`、`idempotent` 等 annotation 有助于 UI 和 risk routing，但它们来自 tool server，可能过时、错误或恶意。真正的 allow/deny 要在可信 host、policy engine 和执行器层根据用户、资源、参数与上下文决定。

每次连接记录 server identity、transport、tool schema、description、版本和 hash。新增工具、参数语义变化、权限范围扩大、描述从“preview”变成“send”时，应触发 diff review 与用户重新确认，而不是沿用旧授权。

高风险调用采用 capability token、参数级 allowlist、dry run 与独立审计。把 tool catalog 当作不可信输入，能避免 prompt injection 通过“新工具描述”绕过策略。
