---
id: report-strongreject
section: report-benchmarks
order: 3
level: S
title: "StrongREJECT：怎样避免把空洞回答误判为成功 jailbreak？"
quick: "我会先问攻击者到底得到了什么。让模型说“好的”不等于得到实质帮助，含糊或无效回答也不能和真正完成有害目标算成一样。StrongREJECT 的价值就在于更认真地评价 jailbreak 输出。"
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
  - title: "StrongREJECT · benchmark / original source"
    url: "https://arxiv.org/abs/2402.10260"
    type: primary
  - title: "Grok 4.7 Model Card"
    url: "https://media.x.ai/v1/website/card4p7-3a96f40b.pdf"
    type: primary
  - title: "Grok 4.6 Model Card"
    url: "https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf"
    type: primary
---

## 题目描述

模型不再拒绝，却只给了含糊、错误或不可用的回答；另一个模型给了实质内容，但 detector 只看拒绝词。

需要讨论：说明 StrongREJECT 的评价动机，以及原 benchmark grader 与 provider compliance 的区别。

## 回答思路

> **Situation：** 模型不再拒绝，却只给了含糊、错误或不可用的回答；另一个模型给了实质内容，但 detector 只看拒绝词。  
> **Task：** 说明 StrongREJECT 的评价动机，以及原 benchmark grader 与 provider compliance 的区别。  
> **Approach / Why：** 检查回答是否真正满足有害目标，固定 rubric 与 grader。  
> **Result / Check：** 对输出质量和拒绝标记分别评价，人工复核分歧。

## 可以这样回答

我会先问攻击者到底得到了什么。让模型说“好的”不等于得到实质帮助，含糊或无效回答也不能和真正完成有害目标算成一样。StrongREJECT 的价值就在于更认真地评价 jailbreak 输出。

但报告写“StrongReject compliance”时，我仍会核对它用了原 grader、改造的 rubric 还是 binary policy judgement。共用数据集不保证评分相同。

复现时会保存 benchmark version、grader model、评分 prompt 与人工抽查结果；再加入正常问题，看是否只是更常拒绝。

## 报告实际采用证据

### StrongREJECT

**类别：** public benchmark + evaluator。**优先级：** P0。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §8.1；PDF p.23 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §9.1；PDF p.35 · `evaluated`。

**读分数时看：** 有害目标相关的 response quality / compliance；需说明 report 采用的 grading。

**适用范围：** 不能把文字拒绝率或 provider 的 binary compliance 与原论文连续评分当同一指标。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 使用公开 behaviors 与固定的 sandbox scoring，不把攻击生成预算藏在评测外。
- **Baselines / Controls：** 比较 refusal-keyword heuristic、原始 grader、provider-style binary rubric 与人工复核。
- **Metrics / Interpretation：** 报告 substantive harmful completion、评分分歧、benign refusal 与评估成本。

## 追问与容易误判的地方

原 benchmark 的连续或细分评价，与某个报告表里的 compliance percentage 不必然可直接转换。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
