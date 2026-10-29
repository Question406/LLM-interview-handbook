---
id: sec-2026-dynamic-long-horizon-evals
section: evaluation
order: 36
level: S
title: "AgentDyn 与 AgentLAB：2026 年的新 benchmark 在挑战什么假设？"
quick: "我会把这几条进展理解为：过去一些 benchmark 把任务和攻击简化得太规整，defense 可能因此看起来很强。AgentDyn 强调动态任务与有用的第三方说明；AgentLAB 强调长期、可适应的交互攻击。"
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
  - title: "AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?"
    url: "https://arxiv.org/abs/2602.03117"
    type: primary
  - title: "AgentLAB: Benchmarking LLM Agents against Long-Horizon Attacks"
    url: "https://arxiv.org/abs/2602.16901"
    type: primary
  - title: "PIArena: A Platform for Prompt Injection Evaluation"
    url: "https://aclanthology.org/2026.acl-long.1533/"
    type: primary
---

## 题目描述

一个 defense 在固定工具序列上很好，但真实 agent 需要动态探索，还会跨多轮接受环境反馈。

需要讨论：区分 dynamic planning、helpful external instructions 与 long-horizon adaptive interaction 的评价价值。

## 回答思路

> **Situation：** 一个 defense 在固定工具序列上很好，但真实 agent 需要动态探索，还会跨多轮接受环境反馈。  
> **Task：** 区分 dynamic planning、helpful external instructions 与 long-horizon adaptive interaction 的评价价值。  
> **Approach / Why：** 用独立轴分别操纵动态性、外部说明和攻击 horizon，再用统一 harness 比较。  
> **Result / Check：** 检查 security 改善是否以拒绝动态任务为代价，并保留完整 trajectories。

## 可以这样回答

我会把这几条进展理解为：过去一些 benchmark 把任务和攻击简化得太规整，defense 可能因此看起来很强。AgentDyn 强调动态任务与有用的第三方说明；AgentLAB 强调长期、可适应的交互攻击。

它们不是可以相互替代的同一个测试。一个检验 agent 是否还会灵活完成任务，另一个追问攻击能否通过多步互动逐渐改变行为。PIArena 则提供 evaluation platform 的参考，方便组织实验，但不会自动消除各 benchmark 的语义差异。

我会做一个小型 factorial study，把这些因素拆开，找出方法失败到底是能力下降、过度防御，还是攻击真正变强。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 建立 static/dynamic × helpful/no-helpful instructions × short/long horizon 的小型受控任务集。
- **Baselines / Ablations：** 比较 prompt defense、plan restriction、model-level defense 和 runtime policy，固定计算预算。
- **Metrics 与判读：** 报告每格 safe completion、ASR、over-defense、token cost 和错误类型；平台适配版本入 manifest。

## 追问与容易误判的地方

最新 benchmark 也可能有实现或构念问题；采用新名字不是 evaluation validity 的保证。

## 论文依据与适用范围

- [AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?](https://arxiv.org/abs/2602.03117) · 2026 · preprint。
- [AgentLAB: Benchmarking LLM Agents against Long-Horizon Attacks](https://arxiv.org/abs/2602.16901) · 2026 · ICML 2026。
- [PIArena: A Platform for Prompt Injection Evaluation](https://aclanthology.org/2026.acl-long.1533/) · 2026 · ACL 2026。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
