---
id: sec-multitenant-agent-isolation
section: privacy
order: 50
level: A
title: "Multi-tenant agent：memory、cache、tools 与 credentials 怎么隔离？"
quick: "我会先把共享状态画出来，尤其是 memory namespaces、retrieval caches、工具结果缓存和 credentials。模型没有主动越权，也可能因为应用层 key 少了 tenant ID 而读到别人的资料。"
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
  - title: "PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action"
    url: "https://arxiv.org/abs/2409.00138"
    type: primary
---

## 题目描述

多个用户共享 agent 服务与部分缓存；某个资源 ID 或 memory result 被错误地复用到其他用户任务。

需要讨论：区分模型层面泄露与应用状态混用，设计 cross-tenant isolation tests。

## 回答思路

> **Situation：** 多个用户共享 agent 服务与部分缓存；某个资源 ID 或 memory result 被错误地复用到其他用户任务。  
> **Task：** 区分模型层面泄露与应用状态混用，设计 cross-tenant isolation tests。  
> **Approach / Why：** 在存储、检索和执行阶段绑定 tenant/user/resource scope，不能只依赖 prompt 写出用户名。  
> **Result / Check：** 交叉运行多个 synthetic tenants，检查接收方实际可见数据与授权。

## 可以这样回答

我会先把共享状态画出来，尤其是 memory namespaces、retrieval caches、工具结果缓存和 credentials。模型没有主动越权，也可能因为应用层 key 少了 tenant ID 而读到别人的资料。

隔离需要在 storage query 和 tool executor 层生效，不能让模型自己记住当前是谁。缓存复用也要满足相同权限与数据可见性条件。

实验用不同 synthetic tenants 的随机 canaries，交错并发任务，再检查是否跨了 resource scope。这样能把 harness bug 与模型受 injection 的问题分开。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 建立至少两个 synthetic tenants，分别测试 retrieval、cache hits、session restoration 与 delegated tools。
- **Baselines / Ablations：** 逐项移除 namespace、resource binding、session identity checks，对照 secure defaults。
- **Metrics 与判读：** 测 cross-tenant exposure、unauthorized writes、缓存正确复用、正常延迟与审计归属。

## 追问与容易误判的地方

Token 或 session ID 不能被当作全部授权依据；资源访问仍需在当前 identity 与 scope 下验证。

## 论文依据与适用范围

- [MCP Security Best Practices · 2025-11-25 documentation](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) · 2025 · official protocol documentation。
- [PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action](https://arxiv.org/abs/2409.00138) · 2024 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
