---
id: mcp-resource-indicator
section: mcp-security
order: 1
level: S
title: MCP 的 OAuth Resource Indicator 和 canonical server URI 为什么必要？Token passthrough 如何造成 confused deputy，服务端应怎样验证并换取下游 token？
quick: "token 必须签发给具体 MCP server。我会让 client 在授权和换 token 时声明 `resource`，server 校验 audience；绝不能把上游 token 原样转给下游。需要下游访问时，由可信 broker 用最小 scope 换取独立、短期 token。"
tags:
  - MCP
  - OAuth
  - Authorization
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: MCP Authorization Specification
    url: https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
    type: primary
---

没有 Resource Indicator，access token 就变成「谁拿到都能用」的万能钥匙。MCP client、authorization server、MCP server 必须对「这个 token 是签给哪一个 resource」有同一 canonical URI。要讲 audience 绑定，以及为什么 passthrough 会变成 confused deputy，不要只背 PKCE。PKCE、HTTPS、refresh rotation 是基础，不替代 audience 校验。MCP Authorization 规范把 resource 当成一等公民，正是为了挡住跨服务滥用。

## 为什么要 resource 与 canonical URI

授权和换 token 时 client 声明 `resource`（目标 MCP server 的规范 URI）。MCP server 校验 issuer、签名、expiry、audience / resource、scope；audience 不匹配必须拒绝。Canonical URI 避免 `localhost`、IP、带尾斜杠的别名让同一服务发出或接受错 token。token 不能像登录 cookie 一样在任意内部 HTTP 请求头里转发。resource 回答「能对谁做」，scope 回答「能做什么」；缺 audience 时 scope 再小也会被拿去打别的服务。日志记录 audience 校验结果，拒绝时不要把 token 原文打进日志。

## Passthrough 与 confused deputy

把用户给 server A 的 bearer 原样转给 server B，B 就能拿这张票去访问 A 或其它接受同一 token 的 API，deputy 被骗着扩大了权限。MCP server 更危险：它既像 API 网关又常被模型驱动。正确做法：server 只消费签给自己的 token；需要下游时，由可信 broker 做 token exchange / delegation，明确下游 audience、最小 scope、短有效期、审计链和用户同意。下游失败不得把上游 token 当 fallback。用户同意一次不能永久转发；下游 audience 变化等于新授权。发布检查应拒绝任何「把入站 token 写出进程」的代码路径。

## 评测要记什么

对抗用例：audience 为 A 的 token 打 B；server 把 Authorization 头转发给第三方；exchange 后 scope 被放大。记录：校验失败码、是否发生转发、下游 token 的 audience 与 TTL。token 面向具体 server；下游访问要换取独立的短期 token；passthrough 就是 confused deputy。代码门禁可以搜入站 `Authorization` 是否被写入出站请求。评测最小集：错 audience 拒绝、透传拦截、exchange 后 audience 与 TTL 符合预期。resource 回答「能对谁做」，scope 回答「能做什么」。

## 追问

- **resource 和 scope 谁更关键？** 都要。scope 是能做什么，resource 是能对谁做；缺 audience 时 scope 再小也会被拿去打别的服务。
- **用户同意一次能否永久转发？** 不能。下游 audience 变化等于新授权。
- **和 elicitation 的关系？** 浏览器里拿到的凭证也必须是给该 server 的；否则钓鱼页会要一张过宽的 token。
