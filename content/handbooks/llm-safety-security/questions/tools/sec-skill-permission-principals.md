---
id: sec-skill-permission-principals
section: tools
order: 17
level: A
title: "SkillGuard：给 skill 单独的 permissions，研究价值在哪里？"
quick: "我会把 skill 当成需要单独限制权限的组件。Agent 总体有写文件能力，不意味着一个只读 skill 可以借用这份能力做任何修改。"
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
  - title: "SkillGuard: A Permission-Centric Framework for Agent Skill Security"
    url: "https://arxiv.org/abs/2606.03024"
    type: primary
---

## 题目描述

同一个 agent 同时加载只读检索 skill 和文件整理 skill；两者不应自动共享全部写权限与外发权限。

需要讨论：设计 skill-scoped principal、manifest 与 runtime enforcement，并解释 context influence 的特殊性。

## 回答思路

> **Situation：** 同一个 agent 同时加载只读检索 skill 和文件整理 skill；两者不应自动共享全部写权限与外发权限。  
> **Task：** 设计 skill-scoped principal、manifest 与 runtime enforcement，并解释 context influence 的特殊性。  
> **Approach / Why：** 把每个 skill 的有效权限与用户授权相交，执行时保留 action 的来源关联。  
> **Result / Check：** 分别验证越权被阻止、权限不足时可完成的任务比例，以及 skill 间权限混用。

## 可以这样回答

我会把 skill 当成需要单独限制权限的组件。Agent 总体有写文件能力，不意味着一个只读 skill 可以借用这份能力做任何修改。

SkillGuard 提醒我们还要看 context influence：skill 即使不直接执行代码，也可能让 agent 以后用别的工具产生 side effects。实验因此需要记录谁引入了目标、哪个 skill 声明了需求、runtime 最终用了什么权限。

我会先做保守的 permission intersection，再研究需要多个 skills 协作时如何显式 delegation；不能因为组合任务难做，就默认把权限合并给所有组件。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 用两个权限不同的 skills 构建单 skill、合法组合和 cross-skill privilege borrowing 三组任务。
- **Baselines / Ablations：** 比较 agent-global permissions、manifest-only 和 runtime-enforced skill scopes。
- **Metrics 与判读：** 测 unauthorized capability use、safe completion、manifest coverage 与用户介入次数。

## 追问与容易误判的地方

Action provenance 可能并不唯一，特别是多个 skills 的内容都在 context 内。需要公开 attribution policy 和不确定时的处理方式。

## 论文依据与适用范围

- [SkillGuard: A Permission-Centric Framework for Agent Skill Security](https://arxiv.org/abs/2606.03024) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
