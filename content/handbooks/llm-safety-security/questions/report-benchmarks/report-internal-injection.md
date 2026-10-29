---
id: report-internal-injection
section: report-benchmarks
order: 16
level: S
title: "报告里的 internal injection evals：怎样读 OpenAI、Claude 与 Gemini 的不同 surfaces？"
quick: "我会按“攻击者能改哪条 observation、想让哪个动作偏离”来读，而不是按实验室名字比较一个百分比。Connector、search、function calls、coding、browser 和 GUI 的攻击面并不相同。"
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
  - title: "GPT-5.6 System Card"
    url: "https://deploymentsafety.openai.com/gpt-5-6"
    type: primary
  - title: "ChatGPT Agent System Card"
    url: "https://deploymentsafety.openai.com/chatgpt-agent"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
  - title: "Gemini 4 Argon Safety & Security Report"
    url: "https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf"
    type: primary
---

## 题目描述

三个实验室都声称 prompt injection 更稳健，却使用不同 attacks、surfaces、harness 和公开程度。

需要讨论：建立能解释差异的配置表，并区分公开 benchmark、内部 suite 与 attack generator。

## 回答思路

> **Situation：** 三个实验室都声称 prompt injection 更稳健，却使用不同 attacks、surfaces、harness 和公开程度。  
> **Task：** 建立能解释差异的配置表，并区分公开 benchmark、内部 suite 与 attack generator。  
> **Approach / Why：** 统一记录 task、entrypoint、attacker access、budget、endpoint 和 safeguards。  
> **Result / Check：** 结果只在对齐的 setting 中比较；公开不足的字段标 unknown。

## 可以这样回答

我会按“攻击者能改哪条 observation、想让哪个动作偏离”来读，而不是按实验室名字比较一个百分比。Connector、search、function calls、coding、browser 和 GUI 的攻击面并不相同。

GPT-Red 是攻击生成方法；Gemini 的多组 held-out suites 包含内部设置和外部 replay；Claude 还要看 fallback 和各种 safeguards。它们可以证明各自测试中的进展，但不构成统一 leaderboard。

我会把公开字段整理成 manifest，缺的就标 unknown。随后用一个公开 benchmark 做共同 anchor，再保留各自特有的内部测试作为补充证据。

## 报告实际采用证据

### GPT-Red

**类别：** attacker model / methodology。**优先级：** P0。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §4.2；2026-08-03 update · `method_used`。

**读分数时看：** 指定 defender queries 下的 attack success，单次 attempt 与累计风险分开。

**适用范围：** 它是攻击生成方法，不是一套与所有 benchmark 等价的固定测试集。

### OpenAI connector / search / function-calling injection evals

**类别：** internal suite。**优先级：** P0。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §4.2 · `evaluated`。
- [ChatGPT Agent System Card](https://deploymentsafety.openai.com/chatgpt-agent) · Prompt injection / robustness sections · `evaluated`。

**读分数时看：** 各 surface 的 attack success / robustness，具体版本见 report。

**适用范围：** Full dataset / harness 不应假设公开；与 Gray Swan scenario reuse 区分。

### Anthropic adaptive coding / computer / browser injection evals

**类别：** internal / partner evaluation suites。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §5.2.2；PDF pp.86–91 · `evaluated`。

**读分数时看：** 固定 surface、attacker budget、harness、fallback 与 safeguards。

**适用范围：** Shade attacker 与 SHADE-Arena benchmark 不同；同名 surface 不保证样本一致。

### Gemini held-out tool / grounding / computer / coding / replay suites

**类别：** mixed internal suites + external replay。**优先级：** P0。

- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §6.1.2；PDF pp.204–212 · `evaluated`。

**读分数时看：** Survival@N attempts，并列合法任务完成情况。

**适用范围：** 五个 suites 的来源与场景不同；只有 external replay 才归入 Gray Swan 证据。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 整理报告的 scenario、surface、payload access、k、attacker model、fallback 与 safeguards。
- **Baselines / Controls：** 用公开任务复现共同设置，再做各 surface 的小型自建 cases；不宣称复现未公开集。
- **Metrics / Interpretation：** 报告预算曲线、safe completion、字段缺失和配置变化；区分 static replay 与 adaptive attack。

## 追问与容易误判的地方

“内部测试”不代表没有价值，也不等于完全可复现；两种判断应分别表述。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
