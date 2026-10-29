---
id: sec-benchmark-selection-matrix
section: evaluation
order: 35
level: S
title: "AgentDojo、InjecAgent、ASB、AgentHarm、SafeArena 应怎样选？"
quick: "我会先停止直接求平均，因为这些名字都包含 agent safety，并不代表测同一件事。AgentDojo 与 InjecAgent 是 indirect injection 的重要入口；ASB 覆盖更广的攻击设置；AgentHarm 关注 harmful tool-assisted requests；SafeArena 把 misuse 放进 web-agent 场景。"
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
  - title: "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents"
    url: "https://arxiv.org/abs/2406.13352"
    type: primary
  - title: "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents"
    url: "https://arxiv.org/abs/2403.02691"
    type: primary
  - title: "Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents"
    url: "https://arxiv.org/abs/2410.02644"
    type: primary
  - title: "AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents"
    url: "https://arxiv.org/abs/2410.09024"
    type: primary
  - title: "SafeArena: Evaluating the Safety of Autonomous Web Agents"
    url: "https://arxiv.org/abs/2503.04957"
    type: primary
---

## 题目描述

你要评估一个 tool-using agent，团队准备把几个 benchmark 的 scores 平均成总 safety 分数。

需要讨论：按 attacker、环境、任务执行方式与 success oracle 比较这些 benchmarks，并选择互补组合。

## 回答思路

> **Situation：** 你要评估一个 tool-using agent，团队准备把几个 benchmark 的 scores 平均成总 safety 分数。  
> **Task：** 按 attacker、环境、任务执行方式与 success oracle 比较这些 benchmarks，并选择互补组合。  
> **Approach / Why：** 先明确构念：indirect injection、user misuse、广义 agent attacks 或 web misuse，再匹配 benchmark。  
> **Result / Check：** 每个 benchmark 单独保留分母与任务完成指标，聚合需要解释权重。

## 可以这样回答

我会先停止直接求平均，因为这些名字都包含 agent safety，并不代表测同一件事。AgentDojo 与 InjecAgent 是 indirect injection 的重要入口；ASB 覆盖更广的攻击设置；AgentHarm 关注 harmful tool-assisted requests；SafeArena 把 misuse 放进 web-agent 场景。

对自己的系统，我会选一个能做动态 tool interactions 的设置、一个 malicious-user 设置，再补系统特有的 memory 或 GUI risks。先检查 evaluator 真正验证了什么，而不是按 benchmark 热度选。

结果表按 setting 分开报告，注明版本、模型、harness 和攻击预算。需要业务汇总分时，再说明如何把这些风险与部署场景对应起来。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 写出产品使用场景与 attacker-control matrix，再为每格选择可覆盖的 benchmark。
- **Baselines / Ablations：** 统一 model/tool interface 的部分尽量统一；无法统一的部分保留单独实验并解释差异。
- **Metrics 与判读：** 并列报告 threat-specific outcomes、task success 与 costs；列出未覆盖场景。

## 追问与容易误判的地方

版本更新可能改变任务数量和 scorer。应 pin 具体版本，避免拿不同论文摘要里的历史数字拼表。

## 论文依据与适用范围

- [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352) · 2024 · NeurIPS 2024。
- [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents](https://arxiv.org/abs/2403.02691) · 2024 · Findings of ACL 2024。
- [Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents](https://arxiv.org/abs/2410.02644) · 2024 · ICLR 2025。
- [AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents](https://arxiv.org/abs/2410.09024) · 2024 · research paper。
- [SafeArena: Evaluating the Safety of Autonomous Web Agents](https://arxiv.org/abs/2503.04957) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
