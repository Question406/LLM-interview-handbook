---
id: mcp-resource-indicator
section: mcp-security
order: 1
level: S
title: MCP 的 OAuth Resource Indicator 和 canonical server URI 为什么必要？Token passthrough 如何造成 confused deputy，服务端应怎样验证并换取下游 token？
quick: "token 必须签发给一个具体的 MCP server，否则谁拿到都能用。我会让 client 在授权和换 token 时声明 `resource`，server 校验 audience，上游 token 绝不原样转给下游；需要下游访问时，由可信 broker 用最小 scope 换一张独立的短期 token。"
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

Resource Indicator 和 canonical server URI 的作用，是让每张 access token 都绑定到一个具体的 MCP server。没有它，token 就是「谁拿到都能用」的万能钥匙；server 再把它原样转给下游，下游拿着这张票就能去打别的服务，这就是 confused deputy。所以 server 只接受签给自己的 token，要访问下游时另外换一张独立的短期 token。

举个例子：用户授权给 server A 一张 bearer token，A 为了调 server B，把 Authorization 头原样转了过去。B 现在手里有一张用户的票，可以拿去访问 A，或者访问其他接受同一 token 的 API。A 这个「代理人」被骗着扩大了权限，而且 MCP server 更危险，它既像 API 网关，又常常被模型驱动。

PKCE、HTTPS、refresh rotation 是基础，但替代不了 audience 校验，面试时别只背 PKCE。MCP Authorization 规范把 resource 当成一等公民，就是为了挡住这种跨服务滥用。

## resource 和 canonical URI 怎么用

授权和换 token 时，client 声明 `resource`，值是目标 MCP server 的规范 URI。MCP client、authorization server、MCP server 三方对「这张 token 签给哪一个 resource」必须用同一个 canonical URI；否则 `localhost`、IP、带尾斜杠的别名会让同一个服务发出或接受错的 token。

MCP server 收到 token 后校验 issuer、签名、expiry、audience / resource 和 scope，audience 不匹配必须拒绝。resource 回答「能对谁做」，scope 回答「能做什么」，缺了 audience，scope 再小也会被拿去打别的服务。token 也不能像登录 cookie 一样，在任意内部 HTTP 请求头里转发。日志记录 audience 校验结果，拒绝时别把 token 原文打进日志。

## 下游访问怎么换 token

正确的做法是：server 只消费签给自己的 token；需要访问下游时，由可信 broker 做 token exchange / delegation，明确下游 audience、最小 scope、短有效期，留下审计链，并取得用户同意。下游失败时，不得拿上游 token 当 fallback。用户同意一次，不代表可以永久转发，下游 audience 一变就等于一次新授权。

发布检查应该拒绝任何「把入站 token 写出进程」的代码路径，代码门禁可以直接搜入站的 `Authorization` 有没有被写进出站请求。

## 评测要记什么

对抗用例至少三条：audience 为 A 的 token 拿去打 B；server 把 Authorization 头转发给第三方；exchange 之后 scope 被放大。最小通过集就是错 audience 被拒绝、透传被拦截、exchange 后的 audience 与 TTL 符合预期。记录里要有校验失败码、是否发生了转发、下游 token 的 audience 和 TTL。

## 追问

**resource 和 scope 谁更关键？**
都要。scope 是能做什么，resource 是能对谁做；缺了 audience，scope 再小也会被拿去打别的服务。

**用户同意一次，能不能永久转发？**
不能。下游 audience 变了就等于新授权。

**和 elicitation 是什么关系？**
浏览器里拿到的凭证也必须是签给这个 server 的，否则钓鱼页会去要一张过宽的 token。见 `mcp-elicitation-secrets`。
