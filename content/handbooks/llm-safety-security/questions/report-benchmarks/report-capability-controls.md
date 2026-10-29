---
id: report-capability-controls
section: report-benchmarks
order: 18
level: S
title: "SWE-bench、Terminal-Bench、OSWorld、MCP-Atlas：为什么安全实验也要看这些？"
quick: "这些 benchmarks 本身主要测能力，但对安全研究很重要。一个不会读网页、不会写文件的 agent，自然也很难完成某些攻击者目标；这不一定说明 defense 好。"
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
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
  - title: "Claude Opus 4.6 System Card"
    url: "https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf"
    type: primary
---

## 题目描述

加了 defense 后 attack success 下降，但 agent 的工具使用和任务完成也明显变差。

需要讨论：设计 capability controls，区分安全收益与失去完成任务的能力。

## 回答思路

> **Situation：** 加了 defense 后 attack success 下降，但 agent 的工具使用和任务完成也明显变差。  
> **Task：** 设计 capability controls，区分安全收益与失去完成任务的能力。  
> **Approach / Why：** 选择与 attack surface 匹配的正常任务，并做 clean/attacked paired evaluation。  
> **Result / Check：** 优先报告 joint safe completion 与 utility matched 的比较。

## 可以这样回答

这些 benchmarks 本身主要测能力，但对安全研究很重要。一个不会读网页、不会写文件的 agent，自然也很难完成某些攻击者目标；这不一定说明 defense 好。

我会按应用选择对照：coding、terminal、computer use、MCP tools 各有对应的正常任务。测试同一 harness 加防御前后能不能完成，并把版本和 cost 一起记录。

最有解释力的是 clean task 能力相当时，受到攻击后的 safe completion 是否提高。不会用某个高 capability score 宣称安全，也不会用单纯拒绝来代表进步。

## 报告实际采用证据

### SWE-bench / Terminal-Bench / OSWorld / MCP-Atlas

**类别：** public task benchmarks / versioned variants。**优先级：** P1。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §8.2 / §8.5 / §8.13.3；PDF pp.175 / 177 / 205 · `evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §2.16 MCP-Atlas；PDF p.28 · `evaluated`。

**读分数时看：** Task completion、strict/partial score、cost 与 tool competence。

**适用范围：** 这些是安全实验的能力对照，不将通过率称为 safety score。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 按 coding/terminal/GUI/MCP surface 选择正常任务，固定版本并构建可配对的受攻击 variants。
- **Baselines / Controls：** 比较原 agent、defense、deny-all 与同等 token/latency budget 的对照。
- **Metrics / Interpretation：** 报告 clean success、attacked safe success、ASR、over-defense 和成本；保留各 benchmark 独立结果。

## 追问与容易误判的地方

报告里的 Terminal-Bench 4.0、OSWorld 2.0 与旧版本有差别，不能只保留 benchmark family 名。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
