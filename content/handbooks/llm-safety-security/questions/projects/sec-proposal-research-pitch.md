---
id: sec-proposal-research-pitch
section: projects
order: 58
level: S
title: "没有直接 agent-security 经历，怎样提出一个可信的 90 秒 research pitch？"
quick: "我会研究“当前 defense 的安全收益，有多少来自让 agent 更少完成任务”。动机是近期动态任务和 outcome-audit 研究都指出，单一 ASR 很容易漏掉这个问题。"
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
  - title: "Ignored, Not Refused: What Low Prompt-Injection Success Rates Hide in Small Tool-Using Agents"
    url: "https://arxiv.org/abs/2610.23254"
    type: primary
  - title: "OSGuard: A Benchmark for Safety in Computer-Use Agents"
    url: "https://arxiv.org/abs/2606.15034"
    type: primary
---

## 题目描述

面试官问你会如何推进 agent safety research，你有可迁移的数据与评测能力，但还没有完成相关实验。

需要讨论：给出具体问题、可证伪 hypothesis、最小 setting、实验对照和预期交付，避免编造经历。

## 回答思路

> **Situation：** 面试官问你会如何推进 agent safety research，你有可迁移的数据与评测能力，但还没有完成相关实验。  
> **Task：** 给出具体问题、可证伪 hypothesis、最小 setting、实验对照和预期交付，避免编造经历。  
> **Approach / Why：** 把文献动机与自己的拟议贡献分开；先提出小而可验证的测量问题。  
> **Result / Check：** 提前说明什么结果会推翻假设，以及下一步会如何调整。

## 可以这样回答

我会研究“当前 defense 的安全收益，有多少来自让 agent 更少完成任务”。动机是近期动态任务和 outcome-audit 研究都指出，单一 ASR 很容易漏掉这个问题。

我的第一步会做一个有 safe path 的小型 tool workflow 集合，配 matched helpful instructions 和 injections。固定模型、harness 和预算，比较几个简单 defenses，分别记录任务完成、违规和 over-defense。

我预期交付的是可重放的数据、可靠 scorer 和一组 failure slices。如果 utility matched 后差异消失，说明原收益可能来自保守策略；如果差异仍保持，就继续研究真正贡献来自哪一层。这是我计划开展的研究，而不是已经取得的结果。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 把问题限制为一个 tool environment、一个 attacker surface 和一个能验证的安全条件，起步预算先固定。
- **Baselines / Ablations：** 至少有 clean、no-defense、deny-all 和被研究 defense；所有 task variants 配对。
- **Metrics 与判读：** 用 raw counts、joint safe completion 与错误归因呈现结果，并预先写下支持/反对 hypothesis 的判断。

## 追问与容易误判的地方

口述里可以说自己的真实可迁移经验，但没有做过的部分一律用 prospective 语气；不要借用论文数字当个人成果。

## 论文依据与适用范围

- [AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?](https://arxiv.org/abs/2602.03117) · 2026 · preprint。
- [Ignored, Not Refused: What Low Prompt-Injection Success Rates Hide in Small Tool-Using Agents](https://arxiv.org/abs/2610.23254) · 2026 · preprint · 2026-10。
- [OSGuard: A Benchmark for Safety in Computer-Use Agents](https://arxiv.org/abs/2606.15034) · 2026 · preprint · revision 2026-10。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
