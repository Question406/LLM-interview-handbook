---
id: mcp-resource-indicator
section: mcp-security
order: 1
level: S
title: MCP 的 OAuth Resource Indicator 和 canonical server URI 为什么必要？Token passthrough 如何造成 confused deputy，服务端应怎样验证并换取下游 token？
quick: token 必须面向具体 MCP server。client 在授权和换 token 时声明 `resource`，server 校验 audience；绝不能把上游 token 原样转给下游。需要下游访问时，由可信 broker 用最小 scope 换取独立、短期 token。
tags:
  - MCP
  - OAuth
  - Authorization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: MCP Authorization Specification
    url: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
    type: primary
---

Resource Indicator 将 access token 绑定到目标 resource server；canonical server URI 让 client、authorization server 和 MCP server 对“这个 token 是给谁的”有同一标识。MCP server 必须验证 issuer、签名、expiry、audience/resource 和 scope。

token passthrough 会把一个本应只给 server A 的 bearer token 交给 server B，B 便可冒充用户访问 A 或扩展权限，形成 confused deputy。服务端不应把拿到的 token 当作通用凭据。

需要访问下游时，使用受控 token exchange / delegation：明确下游 audience、最小 scope、短有效期、审计链与用户同意。PKCE、HTTPS、refresh rotation 是基础，不替代 audience validation。
