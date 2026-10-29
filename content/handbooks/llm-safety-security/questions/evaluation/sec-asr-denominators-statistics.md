---
id: sec-asr-denominators-statistics
section: evaluation
order: 38
level: S
title: "ASR 的分母怎么定？零次成功是否可以宣布零风险？"
quick: "我会把分母直接写在结果旁边。每次 payload 尝试的成功率、每个任务在预算内至少成功一次的比例，以及整个 episode 是否安全，都不是同一个指标。"
companies: []
tags:
  - "Safety / Security Research"
  - "Agentic Security"
  - "研究前沿 2026-10-28"
  - "2026 Research"
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: "The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections"
    url: "https://arxiv.org/abs/2510.09023"
    type: primary
  - title: "Safety, or Just Capability? A Validity Audit of Agent-Safety Benchmarks"
    url: "https://arxiv.org/abs/2607.28685"
    type: primary
---

## 题目描述

两个方法都报告 0% ASR，但一个只测了少量固定任务，另一个包含大量同模板改写和多次重试。

需要讨论：给出 episode-level、attack-trial-level 与 task-level 指标，说明 confidence 与 dependence。

## 回答思路

> **Situation：** 两个方法都报告 0% ASR，但一个只测了少量固定任务，另一个包含大量同模板改写和多次重试。  
> **Task：** 给出 episode-level、attack-trial-level 与 task-level 指标，说明 confidence 与 dependence。  
> **Approach / Why：** 预注册有效样本、exposure 与预算规则，按任务或 template clusters 估计不确定性。  
> **Result / Check：** 同时报告 N、success count、interval、retry policy 和 per-family coverage。

## 可以这样回答

我会把分母直接写在结果旁边。每次 payload 尝试的成功率、每个任务在预算内至少成功一次的比例，以及整个 episode 是否安全，都不是同一个指标。

零成功也只是有限样本观察。在独立 Bernoulli、零成功的简化条件下，95% upper bound 常用约 3/N 的近似；如果样本只是同一个模板的改写，不能把它们当成 N 个独立证据。

因此我更倾向按 task 或 attack family 做 cluster bootstrap，并画随攻击预算变化的成功曲线。所有条件和异常排除都应在看结果前固定。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 预设 attack opportunities、attempt cap、timeout、invalid payload 与 clean-capable subset 的处理。
- **Baselines / Ablations：** 报告 fixed attack 和 best-within-budget 两种结果；按 family 分层重复抽样。
- **Metrics 与判读：** 给出 raw counts、intervals、cluster-level variation、预算曲线与缺失数据；避免只留成功 traces。

## 追问与容易误判的地方

3/N 是说明性近似，要求独立抽样和零成功等前提；它不适合声称对所有未知攻击都存在该上界。

## 论文依据与适用范围

- [The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections](https://arxiv.org/abs/2510.09023) · 2025 · research paper。
- [Safety, or Just Capability? A Validity Audit of Agent-Safety Benchmarks](https://arxiv.org/abs/2607.28685) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
