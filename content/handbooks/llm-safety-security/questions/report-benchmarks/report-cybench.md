---
id: report-cybench
section: report-benchmarks
order: 6
level: A
title: "Cybench：CTF pass@k 可以说明 agent 的哪种能力？"
quick: "Cybench 是理解 cyber capability 的公开入口，尤其适合看不同难度、子任务与 agent scaffold 的影响。它不是 refusal test，也不是模型自己的执行权限评估。"
companies: []
tags:
  - Frontier Report Benchmarks 2026-10-28
  - Safety / Security Research
  - "Benchmark Card"
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: "Cybench · benchmark / original source"
    url: "https://arxiv.org/abs/2408.08926"
    type: primary
  - title: "Claude Opus 4.6 System Card"
    url: "https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf"
    type: primary
---

## 题目描述

一个模型 Cybench pass@30 很高，团队据此判断它能在真实环境里稳定完成长链操作。

需要讨论：解释 CTF、subtasks、hints、scaffold 与 sampling budget 的影响，以及结论应停在哪里。

## 回答思路

> **Situation：** 一个模型 Cybench pass@30 很高，团队据此判断它能在真实环境里稳定完成长链操作。  
> **Task：** 解释 CTF、subtasks、hints、scaffold 与 sampling budget 的影响，以及结论应停在哪里。  
> **Approach / Why：** 把 task difficulty、可用辅助信息和预算拆开，区分 best-within-budget 与单次可靠性。  
> **Result / Check：** 额外测试不同任务与运行环境，不能把 CTF success 当抵抗 injection。

## 可以这样回答

Cybench 是理解 cyber capability 的公开入口，尤其适合看不同难度、子任务与 agent scaffold 的影响。它不是 refusal test，也不是模型自己的执行权限评估。

我会先问 pass@k 的 k 是多少，是否有 hints，能否 web search，以及用什么命令执行环境。高预算下能找到答案，与一次运行就能稳定做完差别很大。

CTF 有明确目标和可验证结果，但现实长链任务还有未知环境、成本与失败恢复。因此它是能力证据的一部分，不是完整风险结论。

## 报告实际采用证据

### Cybench

**类别：** public CTF benchmark。**优先级：** P1。

- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §8.4.7；PDF p.201 · `evaluated`。

**读分数时看：** Task/subtask success、pass@k、可用 hints 与 scaffold。

**适用范围：** 能力评估，不能读成模型拒绝 malicious requests 或 agent 抵抗 injection。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 固定 tasks、source files、tools、hints 与 timeout，在隔离环境重放。
- **Baselines / Controls：** 比较多种 scaffold 与相同预算的重复运行，另设无 hints 条件。
- **Metrics / Interpretation：** 报告 pass@1、budgeted success、subtask coverage、运行成本和失败原因。

## 追问与容易误判的地方

早期模型的人类解题时间对照不应被直接当作当前模型在真实工作的等价工作时长。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
