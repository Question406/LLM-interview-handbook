---
id: report-healthbench
section: report-benchmarks
order: 15
level: A
title: "HealthBench / Professional：为什么属于 safety report，又不是通用 security benchmark？"
quick: "HealthBench 的价值是用专家 rubrics 评估 health 场景中的回答质量与安全表现。Professional 更聚焦 clinicians 的实际任务；它和原始 HealthBench 不是换了个名字的同一份数据。"
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
  - title: "HealthBench / HealthBench Hard · benchmark / original source"
    url: "https://arxiv.org/abs/2505.08775"
    type: primary
  - title: "GPT-5.6 System Card"
    url: "https://deploymentsafety.openai.com/gpt-5-6"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
  - title: "Gemini 4 Argon Safety & Security Report"
    url: "https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf"
    type: primary
  - title: "HealthBench Professional · benchmark / original source"
    url: "https://arxiv.org/abs/2604.27470"
    type: primary
  - title: "Grok 4.7 Model Card"
    url: "https://media.x.ai/v1/website/card4p7-3a96f40b.pdf"
    type: primary
---

## 题目描述

多个 frontier reports 使用 HealthBench，但你的项目研究的是 agent prompt injection。

需要讨论：解释 health rubric 的价值、variants、长度/采样影响，以及与 agent security 的关系。

## 回答思路

> **Situation：** 多个 frontier reports 使用 HealthBench，但你的项目研究的是 agent prompt injection。  
> **Task：** 解释 health rubric 的价值、variants、长度/采样影响，以及与 agent security 的关系。  
> **Approach / Why：** 把 health correctness、communication、safety 与 external-action authorization 分开。  
> **Result / Check：** 固定 variant、grader、verbosity 和 task distribution 后再比较。

## 可以这样回答

HealthBench 的价值是用专家 rubrics 评估 health 场景中的回答质量与安全表现。Professional 更聚焦 clinicians 的实际任务；它和原始 HealthBench 不是换了个名字的同一份数据。

它们在多个模型报告中有直接使用证据，所以值得知道。但高分并不说明 agent 能抵抗不可信网页或不会把健康信息发给错误对象；后两类还需要 injection 与 privacy evaluation。

复现时我会看报告是否做了 length adjustment、用了哪个 grader 和 sampling protocol。长而全面的回答可能更容易覆盖 rubric，也可能带来额外错误，应分别分析。

## 报告实际采用证据

### HealthBench / HealthBench Hard

**类别：** public rubric benchmark。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §5.1 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §8.15.1；PDF p.213 · `evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · Health section；PDF pp.176–178 · `evaluated`。

**读分数时看：** Rubric-based score，指定 Hard / Consensus 等 variant。

**适用范围：** 有 health safety 维度，但不是通用 jailbreak 或 agent authorization benchmark。

### HealthBench Professional

**类别：** public clinician-task benchmark。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §5.1 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §8.15.2；PDF p.213 · `evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · Health；PDF p.177 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §5.1；PDF p.15 · `evaluated`。

**读分数时看：** Clinician-use rubric score；注明长度调整与采样协议。

**适用范围：** 与 HealthBench 是不同分布，不能把 rubric 分数当临床安全概率。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 固定 HealthBench variant 与专业/普通用户场景，保存评分 rubric、grader 和 verbosity。
- **Baselines / Controls：** 比较长度匹配、原始 scoring 与合理的 length adjustment，另设 action/recipient tests。
- **Metrics / Interpretation：** 报告 rubric dimensions、critical errors、uncertainty 与单独的 privacy/authorization outcomes。

## 追问与容易误判的地方

本卡讨论 benchmark 方法，不能把模型分数直接当个体医疗建议的可靠性概率。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
