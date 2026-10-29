---
id: sec-control-protocols-critical-actions
section: alignment
order: 43
level: S
title: "Control protocols：resampling、deferral 与 critical-action checks 各有什么代价？"
quick: "我会先找哪些动作一旦执行就很难补救，把有限的审查预算集中在那里。Resampling 可以帮助暴露可疑行为，deferral 可以把难判断的决定交给更可信组件，但都要测 utility 和成本。"
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
  - title: "Evaluating Control Protocols for Untrusted AI Agents"
    url: "https://arxiv.org/abs/2511.02997"
    type: primary
---

## 题目描述

一个高能力 agent 工作效率很好，但某些写入、外发或权限修改可能带来高影响风险。

需要讨论：设计 trusted monitor / trusted model / human audit 的组合，并面对 adaptive red team。

## 回答思路

> **Situation：** 一个高能力 agent 工作效率很好，但某些写入、外发或权限修改可能带来高影响风险。  
> **Task：** 设计 trusted monitor / trusted model / human audit 的组合，并面对 adaptive red team。  
> **Approach / Why：** 按动作影响分配检查预算，限制对手获取 monitor 内部信号。  
> **Result / Check：** 在同等任务收益和审计预算下测 safety，加入知道 protocol 的攻击者。

## 可以这样回答

我会先找哪些动作一旦执行就很难补救，把有限的审查预算集中在那里。Resampling 可以帮助暴露可疑行为，deferral 可以把难判断的决定交给更可信组件，但都要测 utility 和成本。

Control-protocol 研究显示，红队是否知道检查时机、能否模拟 monitor，会明显改变结果。因此不能只测一个不知 defense 的默认攻击策略。

我会明确哪些信息对 agent 可见，并让红队在这些权限里适应 protocol。最后比较的是固定审查预算下，保住多少正常工作、挡住多少关键违规。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 选含低/高影响动作的 mock tasks，预设 trusted-model 和人工审查预算。
- **Baselines / Ablations：** 比较 random audit、risk-based audit、resampling、critical-action deferral 与 adaptive red teams。
- **Metrics 与判读：** 报告 safe utility、违规拦截、false alarms、审查量及 attacker knowledge 变化下的表现。

## 追问与容易误判的地方

Critical action 的划分本身可能出错：多个低影响 actions 也可能组合成高影响结果，应单独测试。

## 论文依据与适用范围

- [Evaluating Control Protocols for Untrusted AI Agents](https://arxiv.org/abs/2511.02997) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
