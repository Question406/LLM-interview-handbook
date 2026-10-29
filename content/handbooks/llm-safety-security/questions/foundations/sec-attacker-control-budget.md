---
id: sec-attacker-control-budget
section: foundations
order: 2
level: S
title: "如何写一个足够严格、又接近真实部署的 attacker model？"
quick: "我会把 attacker model 当成实验接口写清楚：攻击者能改哪些 bytes，能看见 agent 的哪些状态，能尝试几次，能否观察每次结果，能不能把东西留到下一次 session。"
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
  - title: "Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents"
    url: "https://arxiv.org/abs/2410.02644"
    type: primary
---

## 题目描述

一篇 defense paper 声称能挡住网页攻击，但实验允许攻击者改 system prompt，另一篇只允许改一个 tool response。

需要讨论：列出攻击面、read/write access、可见信息、交互预算、持久化能力与成功条件，给出可比较的实验设置。

## 回答思路

> **Situation：** 一篇 defense paper 声称能挡住网页攻击，但实验允许攻击者改 system prompt，另一篇只允许改一个 tool response。  
> **Task：** 列出攻击面、read/write access、可见信息、交互预算、持久化能力与成功条件，给出可比较的实验设置。  
> **Approach / Why：** 把攻击者能力写成实验配置；改变能力时作为独立实验维度。  
> **Result / Check：** 同预算比较同一攻击面，记录未成功到达注入位置的 episodes。

## 可以这样回答

我会把 attacker model 当成实验接口写清楚：攻击者能改哪些 bytes，能看见 agent 的哪些状态，能尝试几次，能否观察每次结果，能不能把东西留到下一次 session。

比如只改网页正文，与能替换整个 tool response 差别很大；后者可能修改结构化 IDs 或伪造 tool error。若 defense 只允许前一种攻击，就不能把后一种也算进结论。

比较方法时，我会同时固定攻击预算、目标任务和 observable feedback。攻击根本没进入 agent context 的情况会单独统计，避免把没有 exposure 当成成功防御。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 为每个 episode 保存 editable surface、feedback access、trial/token budget、persistence 和 allowed tools。
- **Baselines / Ablations：** 同一目标比较 fixed payload、transfer attack 和 defense-aware adaptive attack；预算分别匹配。
- **Metrics 与判读：** 同时报告 exposure rate、valid attack rate、ASR 与成本；失败尝试进入总预算。

## 追问与容易误判的地方

Black-box 不等于零知识：攻击者可能知道 prompt template 或通过反复 queries 推测 policy。必须具体描述可见信息。

## 论文依据与适用范围

- [The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections](https://arxiv.org/abs/2510.09023) · 2025 · research paper。
- [Agent Security Bench (ASB): Formalizing and Benchmarking Attacks and Defenses in LLM-based Agents](https://arxiv.org/abs/2410.02644) · 2024 · ICLR 2025。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
