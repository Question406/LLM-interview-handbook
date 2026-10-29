---
id: sec-attack-transfer-and-budget
section: injection
order: 12
level: A
title: "Transferable payload 与 per-instance optimized attack，哪种更能说明风险？"
quick: "这两种实验都值得做，但回答的问题不一样。Universal 或 transferable payload 说明一次构造能否影响很多目标；per-instance optimization 说明给定某个目标和反馈，攻击者可以把风险推到多高。"
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
  - title: "The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections"
    url: "https://arxiv.org/abs/2510.09023"
    type: primary
  - title: "WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks"
    url: "https://arxiv.org/abs/2504.18575"
    type: primary
---

## 题目描述

一种攻击对每个任务优化数百次，另一种用同一个 payload 测许多未见任务。

需要讨论：解释二者各自回答的 research question，设计同预算和可部署性比较。

## 回答思路

> **Situation：** 一种攻击对每个任务优化数百次，另一种用同一个 payload 测许多未见任务。  
> **Task：** 解释二者各自回答的 research question，设计同预算和可部署性比较。  
> **Approach / Why：** 分别画 transfer 与 adaptive-budget curves，按任务与环境划分训练和测试。  
> **Result / Check：** 报告 total search cost、unseen success 与 attacker access，避免只展示最佳样本。

## 可以这样回答

这两种实验都值得做，但回答的问题不一样。Universal 或 transferable payload 说明一次构造能否影响很多目标；per-instance optimization 说明给定某个目标和反馈，攻击者可以把风险推到多高。

我会保留两条曲线，而不是硬挑一个胜者。Transfer setting 的测试环境必须真正未见；adaptive setting 要把失败 queries、token 和环境 reset 的成本都算进去。

如果 defense 在低预算下安全，高预算下逐渐失效，这比一个没有预算说明的 ASR 更有解释力。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 按 domain、task template、tool schema 留出测试集，设置固定 payload 与多档 per-instance query budgets。
- **Baselines / Ablations：** 比较 random search、transfer payload、defense-aware search，并匹配总可用预算。
- **Metrics 与判读：** 报告 success-versus-cost、任务覆盖、方差和超预算失败；不只报告 best-of-N 的最终最大值。

## 追问与容易误判的地方

Transfer failure 也可能是工具 schema 或输出格式不兼容；先区分无效 payload 与有效但被防住的攻击。

## 论文依据与适用范围

- [The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections](https://arxiv.org/abs/2510.09023) · 2025 · research paper。
- [WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks](https://arxiv.org/abs/2504.18575) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
