---
id: sec-tool-schema-semantic-authorization
section: tools
order: 14
level: S
title: "JSON schema validation 能防住 tool misuse 吗？"
quick: "Schema 只能证明参数形状正确，不能证明这个 recipient 应该拿到这个 file。我会在执行端把 user、action、resource、destination 和授权上下文一起校验。"
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
  - title: "Design Patterns for Securing LLM Agents against Prompt Injections"
    url: "https://arxiv.org/abs/2506.08837"
    type: primary
  - title: "MCP Security Best Practices · 2025-11-25 documentation"
    url: "https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices"
    type: primary
---

## 题目描述

一个 tool call 完全符合 schema：recipient 是合法 string，attachment 是存在的 file ID，但收件人没有该文件的访问权限。

需要讨论：区分 syntactic validity、resource authorization 和目的限制，提出可组合的执行检查。

## 回答思路

> **Situation：** 一个 tool call 完全符合 schema：recipient 是合法 string，attachment 是存在的 file ID，但收件人没有该文件的访问权限。  
> **Task：** 区分 syntactic validity、resource authorization 和目的限制，提出可组合的执行检查。  
> **Approach / Why：** Schema 之后继续校验 identity、resource ownership、recipient 和当前授权上下文。  
> **Result / Check：** 用 schema-valid unauthorized examples 检查 false negatives，并保留正常跨资源工作流。

## 可以这样回答

Schema 只能证明参数形状正确，不能证明这个 recipient 应该拿到这个 file。我会在执行端把 user、action、resource、destination 和授权上下文一起校验。

可以先用 reference monitor 检查明确规则，再把语义模糊的目的判断交给 monitor 或人工确认。即使模型给了很长的解释，也不能用这段解释覆盖身份和访问控制结果。

测试重点会放在“格式完美但对象错误”的 calls，因为普通 invalid JSON 很容易挡住，却不代表有价值的 security progress。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构建合法 schema 的跨 tenant file IDs、合法收件人与错误附件组合，全部使用隔离 synthetic users。
- **Baselines / Ablations：** 比较 schema-only、role-based access、resource-scoped capabilities 和 purpose-aware checks。
- **Metrics 与判读：** 报告 unauthorized execution、合法操作被拒、delegation 支持率及 decision latency。

## 追问与容易误判的地方

Purpose limitation 难以完全形式化。应公开可表达的 policy 范围，以及需要补充语义判断的部分。

## 论文依据与适用范围

- [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837) · 2025 · research paper。
- [MCP Security Best Practices · 2025-11-25 documentation](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) · 2025 · official protocol documentation。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
