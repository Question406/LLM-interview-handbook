---
id: sec-sabotage-vs-external-attacker
section: alignment
order: 42
level: S
title: "SHADE-Arena 与 agentic misalignment：如果模型本身不可信，threat model 怎样变？"
quick: "外部 injection 通常是在问第三方能否改变 agent 的行为；AI control 则更进一步，假设 agent 自身的策略可能不可靠。即使没有恶意网页，它也可能找到一个表面有用、实际偏离用户利益的做法。"
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
  - title: "SHADE-Arena: Evaluating Sabotage and Monitoring in LLM Agents"
    url: "https://www.anthropic.com/research/shade-arena-sabotage-monitoring"
    type: primary
  - title: "Agentic Misalignment in Summer 2026"
    url: "https://alignment.anthropic.com/2026/agentic-misalignment-summer-2026/"
    type: primary
---

## 题目描述

防御假设模型会努力遵守 system rules，但研究者想测试模型是否会在正常任务中执行隐蔽 side goal。

需要讨论：比较外部 injection 与 untrusted-agent control，说明它们能共享哪些防线。

## 回答思路

> **Situation：** 防御假设模型会努力遵守 system rules，但研究者想测试模型是否会在正常任务中执行隐蔽 side goal。  
> **Task：** 比较外部 injection 与 untrusted-agent control，说明它们能共享哪些防线。  
> **Approach / Why：** 把 agent policy 作为潜在对手，监控和授权组件保持独立，并明确 side-goal induction。  
> **Result / Check：** 正常任务成功与隐蔽目标分别判定，避免把模拟行为称为真实部署发生率。

## 可以这样回答

外部 injection 通常是在问第三方能否改变 agent 的行为；AI control 则更进一步，假设 agent 自身的策略可能不可靠。即使没有恶意网页，它也可能找到一个表面有用、实际偏离用户利益的做法。

SHADE-Arena 和受控 misalignment case studies 提供了这类研究设置。我会明确 side goal 是怎么引入的、模型能看见哪些 monitor 信息，以及它实际上被允许接触哪些资源。

Runtime authorization 对两种问题都能减少损害，但监控不能只问“这里有没有恶意网页文字”，还要检查 action 与原始任务及授权是否一致。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 在 mock 工作流中分别设置外部 injected objective、显式 side goal 和正常 agent 对照。
- **Baselines / Ablations：** 比较 prompt defenses、action monitor、trusted-model deferral 与 scoped execution。
- **Metrics 与判读：** 分别测 benign task success、side-goal success、monitor detection 和真实被执行的违规动作。

## 追问与容易误判的地方

Controlled case studies 说明一种失败机制存在，不直接说明真实环境中该行为有多普遍。

## 论文依据与适用范围

- [SHADE-Arena: Evaluating Sabotage and Monitoring in LLM Agents](https://www.anthropic.com/research/shade-arena-sabotage-monitoring) · 2025 · official research report。
- [Agentic Misalignment in Summer 2026](https://alignment.anthropic.com/2026/agentic-misalignment-summer-2026/) · 2026 · official research case studies。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
