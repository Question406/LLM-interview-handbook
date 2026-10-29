---
id: sec-memorygraft-procedural-learning
section: memory
order: 20
level: A
title: "MemoryGraft：为什么“成功经验”可能比错误知识更危险？"
quick: "我会检查 agent 学到的是事实还是做法。一条记录即使“答案正确”，里面的步骤也可能让以后每次做报告都多读一份不该读的文件。经验库因此不仅能污染知识，还可能改变 policy。"
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
  - title: "MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Experience Retrieval"
    url: "https://arxiv.org/abs/2512.16962"
    type: primary
---

## 题目描述

Agent 会检索过去完成类似任务的经验，并模仿其中的操作步骤；某条经验结果看似成功，但过程包含不必要的敏感操作。

需要讨论：区分 factual retrieval 与 procedural imitation，设计对 memory-based self-improvement 的 security audit。

## 回答思路

> **Situation：** Agent 会检索过去完成类似任务的经验，并模仿其中的操作步骤；某条经验结果看似成功，但过程包含不必要的敏感操作。  
> **Task：** 区分 factual retrieval 与 procedural imitation，设计对 memory-based self-improvement 的 security audit。  
> **Approach / Why：** 分别控制经验的 task outcome、procedure 和来源，而不只检测事实是否正确。  
> **Result / Check：** 在后续未见任务上观察行为迁移，并与没有 experience retrieval 的 agent 对照。

## 可以这样回答

我会检查 agent 学到的是事实还是做法。一条记录即使“答案正确”，里面的步骤也可能让以后每次做报告都多读一份不该读的文件。经验库因此不仅能污染知识，还可能改变 policy。

实验中可以保持旧任务的可见结果一致，只改变中间 procedure，再看检索这条经验是否让后续 agent 复用同样的多余动作。

如果只验证经验里的最终答案，就会把危险 procedure 当成高质量训练信号。安全的经验筛选需要检查执行轨迹及其当时的权限条件。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 建立结果相同但 procedure 不同的历史任务，分别含正常步骤和受控越权步骤。
- **Baselines / Ablations：** 比较 outcome-only memory filter、trajectory-aware filter、no-memory 与 approved-template retrieval。
- **Metrics 与判读：** 测 unsafe procedure reuse、跨任务迁移、正常提效幅度和错误拒绝合法经验的比例。

## 追问与容易误判的地方

一次合法任务里的步骤不一定能迁移到另一用户或资源；经验复用必须重新检查当前授权。

## 论文依据与适用范围

- [MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Experience Retrieval](https://arxiv.org/abs/2512.16962) · 2025 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
