---
id: mcp-elicitation-secrets
section: mcp-security
order: 4
level: A
title: MCP Elicitation 为什么不能用 form 收集 API key、密码或 payment credential？安全的 URL-mode UX / 校验流程该怎样设计？
quick: 秘密不应经过 MCP form 或模型上下文。需要认证时引导用户到可识别的受信任域名完成 OAuth / 支付流程；显示 server identity 和目标域，限制 redirect / URL allowlist，并在返回后只接收最小授权结果。
tags:
  - MCP
  - Elicitation
  - Secrets
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: MCP Elicitation
    url: https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation
    type: primary
---

Elicitation 的 form 看起来像「向用户问一个字段」，但字段会经过 MCP server、client 日志、trace，常常还会进模型上下文和下游工具。密码、API key、卡号一旦走这条路，等于把秘密交给不可信链路。面试官要听的是：秘密只在浏览器可信域完成；MCP 只回收完成 / 取消和最小授权结果。规范把 URL mode 留给认证与支付，不是为了少做一个输入框。好 UX 不是少弹窗，而是用户能看懂谁要什么权限。

## 为什么 form 收集秘密是错的

Form 输入对 server 可见，也对任何记录 elicitation 的调试通道可见。模型为了「帮你填」，可能回显、缓存或把 key 写进另一个 tool 参数。支付凭证还有合规边界，不能进 Agent 宿主。正确分流：非秘密偏好可以用 form；认证、授权、支付必须走 URL mode，把用户送到可识别的官方域。Client 不得把 URL 响应里的 fragment / code 原样喂给模型。Access token 也不能进 chat：只把「已连接某服务」这种状态给模型，调用由 host 持有的凭证发出。一旦 secret 进过 prompt，删除 UI 字段也救不回日志和上下文窗口。

## URL mode 要校验什么

展示给用户：请求方 server 身份、目标域名、用途、scope。Client 校验 HTTPS、域名 allowlist、redirect URI、state / nonce，拒绝任意 URL 把人带到钓鱼页。打开系统浏览器或受控 webview，而不是在模型气泡里嵌一个密码框。取消和超时是正常控制流，不得重试套密。回来后只接收授权完成信号或短寿命、最小 scope 的 token 句柄；仍要验 audience、expiry、scope。可撤销入口必须可见。Allowlist 要钉死，否则 elicitation URL 就是开放重定向。记录：展示过的域名、校验失败原因、secret 是否出现在模型上下文。

## 评测与可被刷点

安全评测应包含：恶意 server 用 form 要 token；URL 指向非 allowlist 域；redirect 到相似域名；完成页把 code 塞进 elicitation 结果。成功标准是拦截且 canary secret 不出现在 prompt / trace。可被刷的点：只测「有个 OAuth 按钮」、不测钓鱼 URL、把减少弹窗当 UX 成功、demo 把 PAT 粘进 form。面试口径：elicitation 可以问偏好，不可以问秘密；秘密走浏览器，token 走 host，模型只看见连接状态。实现上把 form schema 做字段级分类：secret / payment 直接拒绝，强制 URL mode。评测把「form 里出现 password」当成漏洞，而不是 UX 问题。现场能画出 secret 永不经过模型上下文的数据流，比背规范章节更有用。Client 实现上应对 elicitation schema 做静态检查，secret 类字段直接拒绝该请求。日志只留「曾发起 URL mode 到某域」，不留下 token。

## 追问

- **Access token 能不能进 chat？** 不能。只把「已连接某服务」这种状态给模型，调用由 host 持有的凭证发出。
- **为什么 allowlist 要钉死？** 否则 elicitation URL 就是开放重定向，server 可以做钓鱼。
- **和 resource indicator 怎么配合？** 浏览器里发出的 token 必须 audience 绑定该 MCP server，见 `mcp-resource-indicator`。
