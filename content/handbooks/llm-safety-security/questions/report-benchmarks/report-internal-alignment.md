---
id: report-internal-alignment
section: report-benchmarks
order: 17
level: S
title: "Destructive actions、CoT monitoring 与 behavioral audits：怎样避免把观测性当安全性？"
quick: "我会先把“更容易看出来”和“更少发生”分开。一个模型把删除计划说得更清楚，monitorability 可能变好，但删除风险未必下降。反过来，危险事件更少以后，剩下的 positives 太少，也会让 monitor 分数不稳定。"
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
  - title: "CoT monitorability / controllability evaluations · benchmark / original source"
    url: "https://arxiv.org/abs/2512.18311"
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
---

## 题目描述

模型更明确地写出计划，monitor 更容易识别危险动作，monitorability score 因而上升。

需要讨论：解释风险发生率、可观察程度、monitor detection 与 task success 的差别。

## 回答思路

> **Situation：** 模型更明确地写出计划，monitor 更容易识别危险动作，monitorability score 因而上升。  
> **Task：** 解释风险发生率、可观察程度、monitor detection 与 task success 的差别。  
> **Approach / Why：** 将 actor outcomes 和 monitor performance 分成两张表，并记录 positive support。  
> **Result / Check：** 检查真实状态变化、TPR/TNR 与类别稀少带来的不确定性。

## 可以这样回答

我会先把“更容易看出来”和“更少发生”分开。一个模型把删除计划说得更清楚，monitorability 可能变好，但删除风险未必下降。反过来，危险事件更少以后，剩下的 positives 太少，也会让 monitor 分数不稳定。

Destructive actions 需要看是否保护了用户已有改动；确认行为还要区分必要 consent 与无谓中止。每个 outcome 都有自己的 task definition。

研究中我会并列 actor 的真实行为、monitor 的判断，以及正常任务有没有完成，不用某个单一 monitoring 指标替代安全结论。

## 报告实际采用证据

### CoT monitorability / controllability evaluations

**类别：** public methodology + internal environments。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §7.3.1 / §7.3.2 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.6.4.4；PDF p.149 · `evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §3.4.5 · `evaluated`。

**读分数时看：** TPR/TNR-dependent metric、observations、reasoning length 与任务分布。

**适用范围：** Monitorability score 不是 misalignment incidence；与学术 MonitorBench 区分。

### Destructive actions / confirmation-consent / behavioral audits

**类别：** provider-specific internal evaluations。**优先级：** P0。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §3.3 / §3.4 / §7.3.1 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.4 / §6.5.2；PDF pp.104–126 · `evaluated`。

**读分数时看：** 按具体 outcome：protected changes、inappropriate confirmation、misleading claims 等。

**适用范围：** 不同 provider 的行为标签不是同一个 benchmark；不能共用分母或直接排名。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 用有明确状态 oracle 的本地工作流构建 protected edits、合法写入、应确认和不必确认等 cases。
- **Baselines / Controls：** 对比 actions-only、available reasoning、all messages 与 state-aware monitor；实际 outcomes 独立评分。
- **Metrics / Interpretation：** 报告违规率、safe completion、TPR/TNR、positive N、误报与 monitor cost。

## 追问与容易误判的地方

原报告使用的 Guan et al. monitorability suite 与前版题本里的 MonitorBench 不应混称同一个 benchmark。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
