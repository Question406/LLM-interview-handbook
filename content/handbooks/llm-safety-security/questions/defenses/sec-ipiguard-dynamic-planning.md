---
id: sec-ipiguard-dynamic-planning
section: defenses
order: 30
level: S
title: "IPIGuard 与 plan-then-execute：固定 plan 会不会牺牲 agentic utility？"
quick: "固定 plan 可以减少外部文字改写工具序列的机会，但如果任务真的需要临场探索，太刚性的 plan 会让 agent 做不完。这个取舍应该被测出来，而不是藏在选择简单任务里。"
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
  - title: "IPIGuard: A Novel Tool Dependency Graph-Based Defense Against Indirect Prompt Injection in LLM Agents"
    url: "https://arxiv.org/abs/2508.15310"
    type: primary
  - title: "AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?"
    url: "https://arxiv.org/abs/2602.03117"
    type: primary
---

## 题目描述

先固定工具依赖图能限制 injection，但用户的任务需要根据新页面临时决定下一步。

需要讨论：解释 planning/execution 分离的收益，提出不让外部内容自行扩权的受控 replanning。

## 回答思路

> **Situation：** 先固定工具依赖图能限制 injection，但用户的任务需要根据新页面临时决定下一步。  
> **Task：** 解释 planning/execution 分离的收益，提出不让外部内容自行扩权的受控 replanning。  
> **Approach / Why：** 允许数据影响有限参数或选择已授权分支，扩大能力时重新验证 trusted objective 与 policy。  
> **Result / Check：** 在必须动态探索的任务上测 security / utility frontier。

## 可以这样回答

固定 plan 可以减少外部文字改写工具序列的机会，但如果任务真的需要临场探索，太刚性的 plan 会让 agent 做不完。这个取舍应该被测出来，而不是藏在选择简单任务里。

我会把动态变化分层：数据填充参数、在已授权分支间选择，以及新增工具或目的地。前两类可用预先定义的结构表达，最后一类需要新的 policy 检查。

研究问题就是怎样提供足够灵活的 replanning，同时保证外部数据不能把“继续完成原任务”变成“拿到额外权限”。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 在相同任务集合中分别设置 fixed workflow、未知分支与必须发现新操作的任务。
- **Baselines / Ablations：** 比较 unrestricted planning、fixed TDG、bounded branches 和 policy-checked replanning。
- **Metrics 与判读：** 报告 safe completion、blocked legitimate plans、unauthorized plan expansion 与 replanning 成本。

## 追问与容易误判的地方

即使工具序列固定，错误的 resource IDs 或 destinations 仍会违规；需要 separate argument checks。

## 论文依据与适用范围

- [IPIGuard: A Novel Tool Dependency Graph-Based Defense Against Indirect Prompt Injection in LLM Agents](https://arxiv.org/abs/2508.15310) · 2025 · EMNLP 2025。
- [AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?](https://arxiv.org/abs/2602.03117) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
