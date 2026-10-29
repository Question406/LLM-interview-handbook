---
id: sec-reference-monitor-sandbox
section: defenses
order: 34
level: A
title: "Sandbox 已经隔离了代码，为什么 agent 仍可能造成损害？"
quick: "Container 能限制进程看到和影响的环境，但不自动理解“这次任务应该做什么”。如果它挂载了全部工作区、拿到长期凭证、还能外发，agent 仍然可能在隔离内做很多不合适的事。"
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
  - title: "Evaluating Control Protocols for Untrusted AI Agents"
    url: "https://arxiv.org/abs/2511.02997"
    type: primary
---

## 题目描述

代码在 container 中运行，但仍能调用允许的外部服务、修改挂载目录，或用完大量资源。

需要讨论：区分 execution isolation、authorization、egress control 和 resource limits，明确各层保护的对象。

## 回答思路

> **Situation：** 代码在 container 中运行，但仍能调用允许的外部服务、修改挂载目录，或用完大量资源。  
> **Task：** 区分 execution isolation、authorization、egress control 和 resource limits，明确各层保护的对象。  
> **Approach / Why：** 按实际 capability 列出可访问资源，并确保所有 side-effect paths 经过 enforcement。  
> **Result / Check：** 测试允许能力的恶意组合与遗漏路径，记录真实可观察结果。

## 可以这样回答

Container 能限制进程看到和影响的环境，但不自动理解“这次任务应该做什么”。如果它挂载了全部工作区、拿到长期凭证、还能外发，agent 仍然可能在隔离内做很多不合适的事。

我会把文件、网络、凭证、外部 API 和资源预算分别列出来，再看是不是每个 side-effect path 都经过同一套授权检查。模型自愿只用安全工具不算 complete mediation。

研究中还要测试那些本来允许、组合后危险的能力，而不是只演示不能读 container 外一个文件。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 建立 mock workspace、allowlisted sinks、短期 synthetic credentials 和有限资源预算。
- **Baselines / Ablations：** 分别移除 filesystem scope、egress policy、API authorization 与 budget limit，观察各层覆盖。
- **Metrics 与判读：** 报告 unauthorized state changes、synthetic data egress、resource exhaustion、benign task success 与可审计性。

## 追问与容易误判的地方

这一题的安全架构是手册设计。它不声称某篇论文已经证明所有 container / runtime 组合都安全。

## 论文依据与适用范围

- [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837) · 2025 · research paper。
- [Evaluating Control Protocols for Untrusted AI Agents](https://arxiv.org/abs/2511.02997) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
