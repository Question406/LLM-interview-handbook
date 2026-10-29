---
id: sec-egress-indirect-leakage
section: privacy
order: 49
level: A
title: "允许发送正常报告时，如何限制其中夹带的敏感信息？"
quick: "只限制收件人不够，因为这个外部联系人确实有权收到报告，未必有权收到原始记录。我会先明确允许输出哪些信息、统计尺度和用途，再限制 agent 获取和发送不必要的数据。"
companies: []
tags:
  - "Safety / Security Research"
  - "Agentic Security"
  - "研究前沿 2026-10-28"
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: "Defeating Prompt Injections by Design (CaMeL)"
    url: "https://arxiv.org/abs/2503.18813"
    type: primary
  - title: "PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action"
    url: "https://arxiv.org/abs/2409.00138"
    type: primary
---

## 题目描述

Agent 必须把统计报告发给外部合作方，但其 context 里也有不该外发的原始记录。

需要讨论：比较 egress allowlist、data minimization、content inspection 与 information-flow labels 的覆盖范围。

## 回答思路

> **Situation：** Agent 必须把统计报告发给外部合作方，但其 context 里也有不该外发的原始记录。  
> **Task：** 比较 egress allowlist、data minimization、content inspection 与 information-flow labels 的覆盖范围。  
> **Approach / Why：** 限制 destination 之外，还要限制可发送的信息来源与合法 transformations。  
> **Result / Check：** 用 direct、paraphrased、aggregated 和不必要字段的多种 cases 测 disclosure。

## 可以这样回答

只限制收件人不够，因为这个外部联系人确实有权收到报告，未必有权收到原始记录。我会先明确允许输出哪些信息、统计尺度和用途，再限制 agent 获取和发送不必要的数据。

Content inspection 适合拦截一些明确格式；labels 更适合追踪来源；data minimization 则从一开始减少 agent 见到的敏感内容。它们解决不同问题，可以组合。

评估时要放入正常可发的报告，不然把发送功能全禁掉就能轻易得到零泄露。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 使用 synthetic sensitive records，构造可公开聚合与不可外发原始信息的任务。
- **Baselines / Ablations：** 比较 destination-only、regex/DLP、minimal context、flow labels 和组合。
- **Metrics 与判读：** 报告 direct/semantic leakage、合法输出保真度、safe completion 与错误拦截。

## 追问与容易误判的地方

把数据变成摘要或统计不自动使其非敏感；需要按 policy 和剩余推断风险判断。

## 论文依据与适用范围

- [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813) · 2025 · research paper。
- [PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action](https://arxiv.org/abs/2409.00138) · 2024 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
