---
id: report-linux-arena
section: report-benchmarks
order: 11
level: S
title: "LinuxArena：为什么真实工作环境中的 control evaluation 值得关注？"
quick: "LinuxArena 值得读，是因为它把 agent 放在真的有状态、有工具权限的工程环境里。很多问题并不是一句明显危险的话，而是合法操作被组合成了不符合用户利益的结果。"
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
  - title: "LinuxArena · benchmark / original source"
    url: "https://www.redwoodresearch.org/blog/introducing-linuxarena"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
---

## 题目描述

Agent 在真实 Linux 环境做工程任务，拥有不少合法权限；风险不是拒答，而是如何使用这些权限。

需要讨论：比较 LinuxArena 与只判语言输出的测试，提出贴近部署的 control evaluation。

## 回答思路

> **Situation：** Agent 在真实 Linux 环境做工程任务，拥有不少合法权限；风险不是拒答，而是如何使用这些权限。  
> **Task：** 比较 LinuxArena 与只判语言输出的测试，提出贴近部署的 control evaluation。  
> **Approach / Why：** 将正常任务、安全失败条件和 monitor protocol 分开，再检验有权限的恶意组合。  
> **Result / Check：** 同时测 honest utility、side-task completion 与 monitor evasion，保留权限设置。

## 可以这样回答

LinuxArena 值得读，是因为它把 agent 放在真的有状态、有工具权限的工程环境里。很多问题并不是一句明显危险的话，而是合法操作被组合成了不符合用户利益的结果。

我会先弄清具体 main task、side task、可用权限与 monitor，然后再看 actor 能否隐蔽完成 side goal。与纯语言 safety benchmark 相比，这更接近执行系统的控制问题。

但现实感也会增加实验差异。只用其中一小部分任务、换了权限或 monitor，结果就不能被当成原 benchmark 的统一分数。

## 报告实际采用证据

### LinuxArena

**类别：** public privileged-environment control setting。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.2；PDF pp.144–146 · `evaluated`。

**读分数时看：** 在真实 Linux 工作流中的 main/side task outcomes 与监控效果。

**适用范围：** 不同 task subset、privileges 与 monitor 不是同一个实验。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 固定环境 snapshot、task subset、权限与 protocol，保存实际 system state。
- **Baselines / Controls：** 对比 honest actor、side-goal actor、不同 monitors 和 resource-scoped execution。
- **Metrics / Interpretation：** 报告 honest task success、side-task success、undetected violations、审查成本与失败恢复。

## 追问与容易误判的地方

“真实 Linux”不等于真实 production 环境，也不代表评估结论能无条件覆盖部署。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
