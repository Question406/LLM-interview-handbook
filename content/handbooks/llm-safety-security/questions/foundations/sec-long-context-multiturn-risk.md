---
id: sec-long-context-multiturn-risk
section: foundations
order: 5
level: A
title: "长 context 与长期 autonomy 为什么会改变 safety 的评估单位？"
quick: "我会分开两个效应。长 context 可能改变模型对当前指令的理解；长期运行则增加接触风险内容和采取 side effects 的次数。它们都可能让风险上升，但不是同一种机制。"
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
  - title: "Many-shot jailbreaking"
    url: "https://www.anthropic.com/research/many-shot-jailbreaking"
    type: primary
  - title: "AgentLAB: Benchmarking LLM Agents against Long-Horizon Attacks"
    url: "https://arxiv.org/abs/2602.16901"
    type: primary
---

## 题目描述

一个 agent 在单次 tool call 上很稳定，但连续工作数小时后，会读到更多第三方内容并积累更多自主决策。

需要讨论：区分 long-context conditioning 与 repeated exposure，说明如何测 horizon-dependent risk。

## 回答思路

> **Situation：** 一个 agent 在单次 tool call 上很稳定，但连续工作数小时后，会读到更多第三方内容并积累更多自主决策。  
> **Task：** 区分 long-context conditioning 与 repeated exposure，说明如何测 horizon-dependent risk。  
> **Approach / Why：** 分别操纵 context 内容和任务步数，并把 task-level risk 与单步事件联系起来。  
> **Result / Check：** 报告固定 horizon 下的累计事件率、time-to-first-violation 和任务完成情况。

## 可以这样回答

我会分开两个效应。长 context 可能改变模型对当前指令的理解；长期运行则增加接触风险内容和采取 side effects 的次数。它们都可能让风险上升，但不是同一种机制。

在理想独立、每步风险固定为 p 的模型里，N 步至少一次失败是 $1-(1-p)^N$。真实 agent 的步骤通常相关，还会学习和持久化状态，所以这只能做一个说明性 baseline。

实验应分别增加无害 context、增加 adversarial demonstrations、延长任务，以及增加真实 attack exposures，观察风险究竟随什么变化。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构造相同目标的短/长 trajectories，以及相同长度但 benign/adversarial context 的 variants。
- **Baselines / Ablations：** 控制模型、tools、总体 token budget 和有效 injection opportunities，分别比较。
- **Metrics 与判读：** 报告 cumulative violation、first-violation step、per-exposure ASR 与 utility；不要假定独立同分布。

## 追问与容易误判的地方

不能把许多重试只算作一次模型推理成本，也不能只报告最短成功攻击而隐藏全部尝试。

## 论文依据与适用范围

- [Many-shot jailbreaking](https://www.anthropic.com/research/many-shot-jailbreaking) · 2024 · official research report。
- [AgentLAB: Benchmarking LLM Agents against Long-Horizon Attacks](https://arxiv.org/abs/2602.16901) · 2026 · ICML 2026。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
