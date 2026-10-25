---
id: mcp-elicitation-secrets
section: mcp-security
order: 4
level: A
title: MCP Elicitation 为什么不能用 form 收集 API key、密码或 payment credential？安全的 URL-mode UX / 校验流程该怎样设计？
quick: "秘密不应该经过 MCP form 或模型上下文，form 里的字段会进 server、日志、trace，常常还会进上下文。需要认证或支付时，我会走 URL mode，把用户引导到可识别的受信任域名完成 OAuth / 支付，展示 server 身份和目标域，限制 redirect / URL allowlist，回来后只收最小授权结果。"
tags:
  - MCP
  - Elicitation
  - Secrets
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: MCP Elicitation
    url: https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation
    type: primary
---

form 不能收 API key、密码或支付凭证，因为 form 里的字段会经过 MCP server、client 日志、trace，常常还会进模型上下文和下游工具，等于把秘密交给一条不可信的链路。规范把 URL mode 留给认证和支付：秘密只在浏览器的可信域里完成，MCP 只回收「完成 / 取消」和最小的授权结果。

举个例子：一个 server 用 form 让用户「填一下 API key」。用户填了，key 就进了 server 的请求日志和 client 的 trace；模型为了「帮你填」，还可能回显、缓存，或者把 key 写进另一个 tool 的参数。秘密一旦进过输入提示（prompt），事后删掉 UI 字段也救不回日志和上下文窗口。

## 怎么分流

非秘密的偏好可以用 form，认证、授权、支付必须走 URL mode，把用户送到可识别的官方域。支付凭证还有合规边界，本来就不能进 Agent 宿主。实现上，Client 对 elicitation 的字段和类型规范（schema）做静态检查，按字段分类，secret / payment 类字段直接拒绝这个请求，强制改走 URL mode。

URL mode 回来以后也有讲究。Client 不得把 URL 响应里的 fragment / code 原样喂给模型。Access token 也不进对话，只把「已连接某服务」这种状态给模型，真正的调用由 host 持有的凭证发出。

## URL mode 要校验什么

先让用户看懂谁要什么权限：展示请求方 server 的身份、目标域名、用途和 scope。Client 再校验 HTTPS、域名 allowlist、redirect URI、state / nonce，拒绝把人带到钓鱼页的任意 URL。Allowlist 要明确固定下来，否则 elicitation URL 就是一个开放重定向。

打开方式用系统浏览器或受控 webview，别在模型气泡里嵌一个密码框。取消和超时是正常的控制流，不能靠反复重试诱导用户交出秘密。回来后只接收授权完成的信号，或者短寿命、最小 scope 的 token 句柄，并且仍要验 audience、expiry、scope。可撤销的入口必须让用户看得见。

日志只记展示过的域名、校验失败的原因、secret 有没有出现在模型上下文里，比如「曾发起 URL mode 到某域」，token 本身不留。

## 怎么测

安全评测至少包含这几种：恶意 server 用 form 要 token；URL 指向非 allowlist 域；redirect 到相似域名；完成页把 code 塞进 elicitation 结果。通过标准是全部拦截，而且 canary secret 不出现在 prompt / trace 里。「form 里出现 password」直接算漏洞。

容易让评测失真的做法有几种：只测「有个 OAuth 按钮」，不测钓鱼 URL，把弹窗变少当成 UX 成功，demo 里把 PAT 粘进 form。

## 追问

**Access token 能不能进 chat？**
不能。只把「已连接某服务」这种状态给模型，调用由 host 持有的凭证发出。

**为什么 allowlist 要明确固定下来？**
否则 elicitation URL 就是开放重定向，server 可以拿它做钓鱼。

**和 resource indicator 怎么配合？**
浏览器里签发的 token 必须 audience 绑定到这个 MCP server，见 `mcp-resource-indicator`。
