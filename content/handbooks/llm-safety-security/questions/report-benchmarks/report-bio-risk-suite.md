---
id: report-bio-risk-suite
section: report-benchmarks
order: 14
level: A
title: "WMDP、LAB-Bench、VCT、ProtocolQA、FORTRESS：怎样区分 knowledge 与 safeguards？"
quick: "我不会把这些百分比都叫安全分。WMDP 是危险知识的 proxy，LAB-Bench 和 VCT 是研究或领域能力；ProtocolQA Open-Ended 又改了作答形式。它们主要帮助判断模型能做什么。"
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
  - title: "WMDP · benchmark / original source"
    url: "https://arxiv.org/abs/2403.03218"
    type: primary
  - title: "Grok 4.7 Model Card"
    url: "https://media.x.ai/v1/website/card4p7-3a96f40b.pdf"
    type: primary
  - title: "Grok 4.6 Model Card"
    url: "https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf"
    type: primary
  - title: "ProtocolQA Open-Ended · benchmark / original source"
    url: "https://arxiv.org/abs/2407.10362"
    type: primary
  - title: "Virology Capabilities Test (VCT) · benchmark / original source"
    url: "https://arxiv.org/abs/2504.16137"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
  - title: "GPT-5.6 System Card"
    url: "https://deploymentsafety.openai.com/gpt-5-6"
    type: primary
  - title: "FORTRESS / FORTRESS-RN · benchmark / original source"
    url: "https://arxiv.org/abs/2506.14922"
    type: primary
---

## 题目描述

同一张 safety report 既有生物知识 accuracy，也有危险请求 refusal，表面上都是百分比。

需要讨论：区分 capability probes、task adaptations 和 safeguard evaluations，解释高分的不同含义。

## 回答思路

> **Situation：** 同一张 safety report 既有生物知识 accuracy，也有危险请求 refusal，表面上都是百分比。  
> **Task：** 区分 capability probes、task adaptations 和 safeguard evaluations，解释高分的不同含义。  
> **Approach / Why：** 按 knowledge、practical reasoning、harmful compliance、benign refusal 分成独立维度。  
> **Result / Check：** 核对 safeguards on/off、MCQ/open-ended、specific subsets 与 grader。

## 可以这样回答

我不会把这些百分比都叫安全分。WMDP 是危险知识的 proxy，LAB-Bench 和 VCT 是研究或领域能力；ProtocolQA Open-Ended 又改了作答形式。它们主要帮助判断模型能做什么。

FORTRESS 及其报告子集更关注高风险请求下的 safeguards，正常对应问题还用来测 over-refusal。能够回答领域问题，与是否愿意帮助不允许的用途，需要分别看。

讨论这些测试时，我会停在 evaluation design：设置、可复现性和指标，不从一个知识准确率直接推断现实危害，也不展开操作性危险内容。

## 报告实际采用证据

### WMDP

**类别：** public multiple-choice proxy。**优先级：** P1。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.5；PDF p.22 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §8.4；PDF p.33 · `evaluated`。

**读分数时看：** Bio/Chem/Cyber 子集 accuracy。

**适用范围：** 危险知识 proxy，与 refusal / safeguard effectiveness 分开解释。

### LAB-Bench

**类别：** public benchmark。**优先级：** P1。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.6；PDF p.22 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §8.5；PDF p.34 · `evaluated`。

**读分数时看：** 按实际使用的 practical / 子任务 split 报 accuracy。

**适用范围：** 通用生物研究能力，不自动等于 harmful uplift。

### Virology Capabilities Test (VCT)

**类别：** public multimodal benchmark。**优先级：** P1。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §2.2.3.1；PDF pp.20–21 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.2；PDF p.21 · `evaluated`。

**读分数时看：** 按具体 release 的 expert-graded accuracy。

**适用范围：** Biology knowledge 与安全拒绝不同；Biosecurity VCT 是报告中另列的 internal companion。

### ProtocolQA Open-Ended

**类别：** report-adapted task variant。**优先级：** P1。

- [GPT-5.6 System Card](https://deploymentsafety.openai.com/gpt-5-6) · §9.1.1.2 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §7.7；PDF p.22 · `evaluated`。

**读分数时看：** Free-text protocol troubleshooting accuracy。

**适用范围：** 不能把 open-ended variant 当成原 multiple-choice task 的同一分数。

### FORTRESS / FORTRESS-RN

**类别：** public benchmark + report subset。**优先级：** P1。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §9.3；PDF p.25 · `evaluated_adapted`。

**读分数时看：** Harmful-risk rubric 与 benign counterpart 的 over-refusal；报告注明 RN subset。

**适用范围：** FORTRESS-RN 不能代表完整 FORTRESS；accuracy / refusal / risk score 需分别解释。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 只分析公开安全过滤后的 benchmark、元数据与评分协议，固定具体 subset。
- **Baselines / Controls：** 把能力条件与 safeguards 条件分开；比较 MCQ/open-ended 与 benign/harmful pairs。
- **Metrics / Interpretation：** 报告 accuracy、harmful compliance、benign refusal、专家基线的可比性及未覆盖风险。

## 追问与容易误判的地方

Biosecurity VCT、FORTRESS-RN 与完整 VCT、FORTRESS 不是同一项测试；report suffix 应进入 manifest。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
