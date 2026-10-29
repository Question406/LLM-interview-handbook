---
id: sec-mcp-confused-deputy
section: tools
order: 15
level: A
title: "MCP confused deputy：知道“谁登录了”为什么还不够？"
quick: "我会问代理究竟在替谁做事。User identity、发起请求的 client，以及下游 API resource 是不同对象，不能因为用户曾经登录过就把所有后续请求都视为授权。"
companies: []
tags:
  - "Safety / Security Research"
  - "Agentic Security"
  - "研究前沿 2026-10-28"
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: "MCP Security Best Practices · 2025-11-25 documentation"
    url: "https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices"
    type: primary
---

## 题目描述

MCP proxy 代表用户访问下游服务，但多个 clients 共用代理，授权结果可能被错误地复用到别的 client 或 resource。

需要讨论：解释 authentication、delegation 与 token audience 的区别，并描述最小可验证系统。

## 回答思路

> **Situation：** MCP proxy 代表用户访问下游服务，但多个 clients 共用代理，授权结果可能被错误地复用到别的 client 或 resource。  
> **Task：** 解释 authentication、delegation 与 token audience 的区别，并描述最小可验证系统。  
> **Approach / Why：** 绑定 user、client、target resource 与授权操作；分别验证各段 token 和 consent。  
> **Result / Check：** 在跨 client、跨 resource、过期与错误 audience 的测试中确认请求在 side effect 前被拒。

## 可以这样回答

我会问代理究竟在替谁做事。User identity、发起请求的 client，以及下游 API resource 是不同对象，不能因为用户曾经登录过就把所有后续请求都视为授权。

按照 MCP security guidance，需要认真检查 token audience、授权流程里的 client 关系和下游访问控制，也不能把收到的任意 bearer token 直接当作下游凭证转发。

研究实验可以放在一个完全 mock 的 proxy：只改变 client 或 resource，看看同一个看似有效的授权是否被错误复用。这里测的是 delegation implementation，不是模型能否识别一句 malicious text。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 用两个 mock clients、两个 mock resources 和独立 synthetic tokens 建立 proxy testbed。
- **Baselines / Ablations：** 分别去掉 audience check、client binding、consent binding；保留其他设置一致。
- **Metrics 与判读：** 检查跨 client/resource 的 unauthorized request、正常 delegated task success 和审计可追踪性。

## 追问与容易误判的地方

具体 MUST/SHOULD 约束以引用的 versioned documentation 为准；本题的 mock 设置是研究设计，不是完整 OAuth 实现。

## 论文依据与适用范围

- [MCP Security Best Practices · 2025-11-25 documentation](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) · 2025 · official protocol documentation。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
