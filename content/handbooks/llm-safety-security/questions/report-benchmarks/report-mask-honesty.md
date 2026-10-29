---
id: report-mask-honesty
section: report-benchmarks
order: 12
level: S
title: "MASK / MASK-Rectified：honesty 为什么不能用 factual accuracy 替代？"
quick: "我会先问模型原本表达的 belief 是什么。MASK 试图把“知道却被压力引导说了另一套”与“根本不知道”分开，所以它测的不是普通知识准确率。"
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
  - title: "MASK / MASK-Rectified · benchmark / original source"
    url: "https://arxiv.org/abs/2503.03750"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
  - title: "Grok 4.7 Model Card"
    url: "https://media.x.ai/v1/website/card4p7-3a96f40b.pdf"
    type: primary
  - title: "Grok 4.6 Model Card"
    url: "https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf"
    type: primary
---

## 题目描述

模型知道一个答案，却在 user 或 system pressure 下给了相反说法；另一个模型只是知识不足答错。

需要讨论：解释先 eliciting beliefs 再测试 pressured statements 的逻辑，以及 roleplay、evasion 的处理。

## 回答思路

> **Situation：** 模型知道一个答案，却在 user 或 system pressure 下给了相反说法；另一个模型只是知识不足答错。  
> **Task：** 解释先 eliciting beliefs 再测试 pressured statements 的逻辑，以及 roleplay、evasion 的处理。  
> **Approach / Why：** 区分 knowledge、stated belief 和 honesty under pressure，固定 scorer 版本。  
> **Result / Check：** 把 exclusions、abstention 与 denominator 一起报告。

## 可以这样回答

我会先问模型原本表达的 belief 是什么。MASK 试图把“知道却被压力引导说了另一套”与“根本不知道”分开，所以它测的不是普通知识准确率。

Claude 报告使用 MASK，而 Grok 报告明确写了 MASK-Rectified，修改了某些 roleplay 判定。这是阅读 tech report 时很容易漏掉的 suffix：同名数据，不同 grader 可能改变结论。

我会同时报告 scored count、evasion、没有稳定 belief 的样本，以及不同 pressure 来源。只对愿意明确作答的 subset 计算 honesty，也要说明被排除了谁。

## 报告实际采用证据

### MASK / MASK-Rectified

**类别：** public benchmark + provider adaptation。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §6.5.4.2；PDF p.130 · `evaluated`。
- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §11.1；PDF p.26 · `evaluated_adapted`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §12.1；PDF p.38 · `evaluated_adapted`。

**读分数时看：** Stated belief 与 pressured response 的 contradiction / honesty；记录 exclusions。

**适用范围：** MASK-Rectified 修改 roleplay 判定；不同评分版本和方向不能直接对比。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 固定 public split，保存 belief elicitation 与 pressured response 的完整 pairing。
- **Baselines / Controls：** 比较原始 grader、roleplay-aware grading 和人工复核，并按 pressure 来源分层。
- **Metrics / Interpretation：** 报告 honesty、accuracy、abstention/evasion、exclusions 和各自分母。

## 追问与容易误判的地方

MASK 分数不直接证明长期 strategic deception，也不等于模型始终忠于用户目标。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
