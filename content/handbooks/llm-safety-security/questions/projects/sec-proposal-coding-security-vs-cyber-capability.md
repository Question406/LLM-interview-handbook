---
id: sec-proposal-coding-security-vs-cyber-capability
section: projects
order: 57
level: A
title: "Research proposal：coding agent 的 functional tests、security tests 与 cyber capability 怎么分？"
quick: "我会把三个问题分开：它能不能写出正确功能，代码会不会引入安全问题，以及它自己会不会越过允许的操作范围。CyberGym 主要帮助研究 vulnerability reproduction capability，SusVibes 则提醒我们功能通过与代码安全并不相同。"
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
  - title: "Is Vibe Coding Safe? Benchmarking Vulnerability of Agent-Generated Code in Real-World Tasks"
    url: "https://arxiv.org/abs/2512.03262"
    type: primary
  - title: "CyberGym: Evaluating AI Agents' Real-World Cybersecurity Capabilities at Scale"
    url: "https://arxiv.org/abs/2506.02548"
    type: primary
---

## 题目描述

Coding agent 能通过 feature tests，也能在漏洞评估中取得高分，但团队想知道它生成的代码是否适合安全部署。

需要讨论：区分代码安全、漏洞分析能力与 agent 自身受控性，并设计互补的评价。

## 回答思路

> **Situation：** Coding agent 能通过 feature tests，也能在漏洞评估中取得高分，但团队想知道它生成的代码是否适合安全部署。  
> **Task：** 区分代码安全、漏洞分析能力与 agent 自身受控性，并设计互补的评价。  
> **Approach / Why：** 把 functional correctness 与 security properties 分开评分，所有运行使用隔离的授权测试环境。  
> **Result / Check：** 检查通过功能测试但违反安全约束的比例，避免把 cyber benchmark 分数当作整体安全结论。

## 可以这样回答

我会把三个问题分开：它能不能写出正确功能，代码会不会引入安全问题，以及它自己会不会越过允许的操作范围。CyberGym 主要帮助研究 vulnerability reproduction capability，SusVibes 则提醒我们功能通过与代码安全并不相同。

我会挑小规模、可本地重放的 repository tasks，分别设置 functional tests 和明确的 security checks，再检查 agent 是否投机修改测试或接触不该接触的评测信息。

研究价值在于建立这几类结果的关系，而不是宣称某个单一分数代表安全。漏洞重现的能力可以用于防御研究，但不自动说明 agent 本身可靠。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 在隔离授权环境选择 repository tasks，固定版本，隐藏评测答案并保存 agent action trace。
- **Baselines / Ablations：** 比较正常 agent、安全提示、独立 code review 和 security-specific tests；运行预算一致。
- **Metrics 与判读：** 分别报告 functional pass、secure pass、joint pass、测试完整性和 execution-scope violations。

## 追问与容易误判的地方

本题讨论 evaluation design，不执行真实外部目标攻击；benchmark 版本变化时重新核对任务和评分定义。

## 论文依据与适用范围

- [Is Vibe Coding Safe? Benchmarking Vulnerability of Agent-Generated Code in Real-World Tasks](https://arxiv.org/abs/2512.03262) · 2025 · ICML 2026 · revision 2026-09。
- [CyberGym: Evaluating AI Agents' Real-World Cybersecurity Capabilities at Scale](https://arxiv.org/abs/2506.02548) · 2025 · research paper · revision 2026-03。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
