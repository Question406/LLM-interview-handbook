---
id: sec-safe-completion-objective
section: foundations
order: 6
level: S
title: "Safety 是 refusal，还是在约束下完成任务？如何定义 safe completion？"
quick: "我会把 safe completion 定义成两件事同时成立：完成用户目标，并且全过程满足任务约束。前者用 task evaluator，后者检查 action trace 和最终环境状态。"
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
  - title: "OSGuard: A Benchmark for Safety in Computer-Use Agents"
    url: "https://arxiv.org/abs/2606.15034"
    type: primary
---

## 题目描述

购物 agent 因为网页有第三方说明就停止购买；另一个顺利下单却忽略了用户的预算和地址限制。

需要讨论：给出既不能靠全拒绝取巧、又能检测不安全 shortcut 的 success definition。

## 回答思路

> **Situation：** 购物 agent 因为网页有第三方说明就停止购买；另一个顺利下单却忽略了用户的预算和地址限制。  
> **Task：** 给出既不能靠全拒绝取巧、又能检测不安全 shortcut 的 success definition。  
> **Approach / Why：** 将 task success 与 policy satisfaction 分开评分，再计算 joint safe completion。  
> **Result / Check：** 四种 task/safety outcomes 都要保留，超时和基础能力失败另作诊断。

## 可以这样回答

我会把 safe completion 定义成两件事同时成立：完成用户目标，并且全过程满足任务约束。前者用 task evaluator，后者检查 action trace 和最终环境状态。

这样就会得到四格：完成且安全、完成但违规、没完成但安全、没完成且违规。全部拒绝会落在“没完成但安全”，不会被当成最好的 agent。

Helpful third-party instructions 是很好的测试：网页告诉你如何选尺码可能确实有用，系统需要利用它完成任务，同时不允许它修改预算或授权。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构造必须读取第三方步骤才能完成的任务，确保每个 risk variant 仍有一条安全完成路径。
- **Baselines / Ablations：** 比较 unrestricted agent、block-all-external-content、learned defense 和 action enforcement。
- **Metrics 与判读：** 报告四格 outcome matrix、safe completion、over-defense、latency 与 intervention 次数。

## 追问与容易误判的地方

有些任务本身不可安全完成。它们应有单独的正确拒绝标签，不能与存在安全路径的任务混算。

## 论文依据与适用范围

- [AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?](https://arxiv.org/abs/2602.03117) · 2026 · preprint。
- [OSGuard: A Benchmark for Safety in Computer-Use Agents](https://arxiv.org/abs/2606.15034) · 2026 · preprint · revision 2026-10。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
