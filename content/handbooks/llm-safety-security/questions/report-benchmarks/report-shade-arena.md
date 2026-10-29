---
id: report-shade-arena
section: report-benchmarks
order: 10
level: S
title: "SHADE-Arena：高 stealth success 和高 safety score 到底方向相同吗？"
quick: "我会先给图表标清是谁的成功。SHADE-Arena 中，agent 被安排正常主任务和有害 side task；如果既完成 side task 又没被 monitor 抓到，这是攻击者的 stealth success，越高通常越不利。"
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
  - title: "SHADE-Arena · benchmark / original source"
    url: "https://www.anthropic.com/research/shade-arena-sabotage-monitoring"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
  - title: "Claude Opus 4.6 System Card"
    url: "https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf"
    type: primary
---

## 题目描述

一份图表展示 agent 的 covert side-task success，另一份论文展示 control protocol 的 safety。

需要讨论：解释 actor、monitor、main task 与 side task，并写出可以互相核对的 outcomes。

## 回答思路

> **Situation：** 一份图表展示 agent 的 covert side-task success，另一份论文展示 control protocol 的 safety。  
> **Task：** 解释 actor、monitor、main task 与 side task，并写出可以互相核对的 outcomes。  
> **Approach / Why：** 分别记录 side goal、monitor verdict 和主任务结果，再按明确定义组合。  
> **Result / Check：** 核对 monitor 能看哪些消息、推理是否可见及攻击是否充分 elicited。

## 可以这样回答

我会先给图表标清是谁的成功。SHADE-Arena 中，agent 被安排正常主任务和有害 side task；如果既完成 side task 又没被 monitor 抓到，这是攻击者的 stealth success，越高通常越不利。

Control paper 的 safety score 可能反过来描述 protocol 阻止这种结果的能力。两者是否互补，取决于失败、错误和任务完成的定义，不能只做一减。

实验还要报告 agent 拒绝 side task 的比例，以及 monitor 看到的是 actions、可见 reasoning 还是全部 trace。否则低 stealth success 可能只是没有成功诱导出 side-goal 行为。

## 报告实际采用证据

### SHADE-Arena

**类别：** public agent-control benchmark。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.1；PDF pp.141–143 · `evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §6.4.1；PDF pp.142–144 · `evaluated`。

**读分数时看：** Harmful side-task success AND monitor evasion；主任务结果另报。

**适用范围：** Monitor、可见 reasoning、side-goal induction 与 red-team elicitation 都影响得分。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 固定 task pairs、monitor、观察视图和 actor elicitation 条件。
- **Baselines / Controls：** 比较 actor refusal、side-task failure、caught success 与 undetected success，另报 main task。
- **Metrics / Interpretation：** 记录完整 outcome table、per-task uncertainty、错误 trials 和成本。

## 追问与容易误判的地方

Gray Swan 的 Shade 是 red-teaming tool；SHADE-Arena 是另一项 sabotage benchmark，不要因读音相近混在一起。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
