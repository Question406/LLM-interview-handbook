---
id: report-bbq
section: report-benchmarks
order: 13
level: S
title: "BBQ：为什么 ambiguous accuracy、disambiguated accuracy 和 bias score 都要看？"
quick: "我会先区分信息够不够。Ambiguous context 里选择 unknown 可能正确；disambiguated context 已经提供证据，继续选 unknown 就是没利用信息。"
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
  - title: "BBQ · benchmark / original source"
    url: "https://arxiv.org/abs/2110.08193"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
  - title: "Claude Opus 4.6 System Card"
    url: "https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf"
    type: primary
---

## 题目描述

一个模型 bias score 很接近零，但它可能是在所有问题上都选择 unknown。

需要讨论：解释两种 context 和不同指标如何共同识别 stereotypes、知识利用与保守策略。

## 回答思路

> **Situation：** 一个模型 bias score 很接近零，但它可能是在所有问题上都选择 unknown。  
> **Task：** 解释两种 context 和不同指标如何共同识别 stereotypes、知识利用与保守策略。  
> **Approach / Why：** 用有/无足够信息的 paired questions，检查证据改变后答案是否跟着变。  
> **Result / Check：** 同时看 accuracy、bias direction 与 subgroup 样本量。

## 可以这样回答

我会先区分信息够不够。Ambiguous context 里选择 unknown 可能正确；disambiguated context 已经提供证据，继续选 unknown 就是没利用信息。

所以 bias score 靠近零并不能独立说明好。它可能是准确，也可能是随机或一概回避。Claude 报告把这些指标一起展示，是我们应该保留的阅读方式。

如果研究 agent fairness，还得增加真实动作测试，比如谁被推荐、谁获得资源。QA 中少用 stereotype 是重要证据，但不是全部公平性。

## 报告实际采用证据

### BBQ

**类别：** public QA benchmark。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §4.4.2；PDF pp.75–76 · `evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · Bias Benchmark for QA；PDF pp.71–72 · `evaluated`。

**读分数时看：** Ambiguous/disambiguated accuracy 与 bias score。

**适用范围：** QA stereotypes 与真实 agent 的 allocation / action fairness 分别测。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 运行固定 split 和 prompt format，按 ambiguous/disambiguated、维度与群体分层。
- **Baselines / Controls：** 比较 unknown-only、random、普通模型与 intervention，检查 evidence sensitivity。
- **Metrics / Interpretation：** 报告两类 accuracy、bias score、置信范围和 subgroup N；另测 agent action outcomes。

## 追问与容易误判的地方

原始 benchmark 以特定语言文化背景构建；跨语言翻译需要重新检查语义与标签，而非机械套用。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
