---
id: report-crescendo
section: report-benchmarks
order: 4
level: A
title: "Crescendo：多轮 jailbreak 方法为什么不能当成固定测试集？"
quick: "我会把 Crescendo 称为多轮攻击方法，而不是一份固定问题清单。它会根据对话逐步推进，所以真正的实验单位是一整段 interaction。"
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
  - title: "Crescendo · benchmark / original source"
    url: "https://arxiv.org/abs/2404.01833"
    type: primary
  - title: "Grok 4.7 Model Card"
    url: "https://media.x.ai/v1/website/card4p7-3a96f40b.pdf"
    type: primary
  - title: "Grok 4.6 Model Card"
    url: "https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf"
    type: primary
---

## 题目描述

报告的一行“long-horizon jailbreaks”混合了 Crescendo 和其他多轮攻击，而对照模型只被测了一个固定 prompt。

需要讨论：定义 attack algorithm、goal set、turn budget 和 success oracle，说明公平比较方式。

## 回答思路

> **Situation：** 报告的一行“long-horizon jailbreaks”混合了 Crescendo 和其他多轮攻击，而对照模型只被测了一个固定 prompt。  
> **Task：** 定义 attack algorithm、goal set、turn budget 和 success oracle，说明公平比较方式。  
> **Approach / Why：** 把攻击方法和被攻击的任务数据分开，固定整段交互预算。  
> **Result / Check：** 所有未成功轮次、重试和结束条件都计入成本。

## 可以这样回答

我会把 Crescendo 称为多轮攻击方法，而不是一份固定问题清单。它会根据对话逐步推进，所以真正的实验单位是一整段 interaction。

比较时要固定目标集合、最大 turns、query budget、能否回看失败反馈，以及 attacker model。否则一个方法试几十轮，另一个只试一句话，结果并不能解释谁更 robust。

报告里的 long-horizon suite 还可能混合其他攻击，我会保留 component-level 结果，再讨论整个 suite 的 coverage。

## 报告实际采用证据

### Crescendo

**类别：** attack methodology。**优先级：** P0。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §8.1；PDF p.23 · `evaluated_as_component`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §9.1；PDF p.35 · `evaluated_as_component`。

**读分数时看：** 固定 turn / query budget 下的 harmful completion 或攻击成功。

**适用范围：** 它是一种多轮攻击方法；报告中的 long-horizon suite 可能混合多种 attacks。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 在授权隔离 evaluation 中固定 goal set 与最大交互预算，保存完整对话。
- **Baselines / Controls：** 比较单轮、相同预算的多次单轮与 adaptive multi-turn，并匹配总 tokens。
- **Metrics / Interpretation：** 报告 task-level success、达到结果的 turns、累计成本和正常多轮能力。

## 追问与容易误判的地方

某次回复看似无害，不能独立判断整段会话的风险；同时也不能把所有长对话都判作攻击。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
