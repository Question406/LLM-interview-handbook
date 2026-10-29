---
id: sec-firewall-saturation-replication
section: evaluation
order: 41
level: A
title: "一篇论文说 firewall 达到 perfect security，你会怎样复现和挑战？"
quick: "我会把这个结果当成值得复现的信号。先固定原版本和攻击设置，确认数值；再检查失败攻击究竟被什么阻止，以及正常任务是否仍然完成。"
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
  - title: "Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?"
    url: "https://arxiv.org/abs/2510.05244"
    type: primary
  - title: "The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections"
    url: "https://arxiv.org/abs/2510.09023"
    type: primary
---

## 题目描述

一个简单 tool-interface defense 在多个公开 benchmark 上几乎没有攻击成功。

需要讨论：判断是 defense 本身强、攻击弱、scorer 有问题，还是任务允许简单保守策略取巧。

## 回答思路

> **Situation：** 一个简单 tool-interface defense 在多个公开 benchmark 上几乎没有攻击成功。  
> **Task：** 判断是 defense 本身强、攻击弱、scorer 有问题，还是任务允许简单保守策略取巧。  
> **Approach / Why：** 先精确复现，再审计 evaluator 与 utility，最后按公开 threat model 增强攻击。  
> **Result / Check：** 在有用第三方说明、dynamic planning 与 defense-aware attacks 上检查结果是否保持。

## 可以这样回答

我会把这个结果当成值得复现的信号。先固定原版本和攻击设置，确认数值；再检查失败攻击究竟被什么阻止，以及正常任务是否仍然完成。

接下来会根据论文允许的 attacker access 做 adaptive testing，而不是随意给攻击者更强权限。如果增加能力，需要作为新的 setting 报告。

同时补动态任务、真正需要外部 instructions 的 cases 和工具参数层面的违规。最后的结论可能是方法确实有效，也可能是 benchmark 已经不能区分方法；两者都是有价值的研究发现。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 先跑原 benchmark commit、defense config 与 scorer，再建少量人工核实的 edge cases。
- **Baselines / Ablations：** 分别测试原攻击、同权限 adaptive attacks、dynamic tasks 和 deny-all-external baseline。
- **Metrics 与判读：** 报告逐阶段失败原因、safe completion、over-defense 与 implementation fixes 前后的差异。

## 追问与容易误判的地方

来源论文自己也讨论 benchmark limitations；引用“perfect”时需要同时保留其指定实验范围。

## 论文依据与适用范围

- [Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?](https://arxiv.org/abs/2510.05244) · 2025 · research paper。
- [The Attacker Moves Second: Stronger Adaptive Attacks Bypass Defenses Against LLM Jailbreaks and Prompt Injections](https://arxiv.org/abs/2510.09023) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
