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
updatedAt: 2026-08-17
sources:
  - title: MCP Elicitation
    url: https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation
    type: primary
---

form input 易被 server、client log、trace、模型上下文或下游工具看到，不能用于 password、API key、卡号等 credential。秘密授权应在浏览器的可信 domain 完成，MCP client 只处理完成/取消和受限 token 结果。

URL mode 要向用户明确显示请求方、目标域、用途和 scope；client 验证 HTTPS、allowlist、redirect、state/nonce，并防止任意 URL 将用户带到钓鱼站。取消和超时必须是正常控制流。

回来后仍应执行 audience、expiry、scope 和最小权限校验。好的 UX 不是少弹窗，而是让用户能看懂“谁要什么权限、给到哪里、能否撤销”。
