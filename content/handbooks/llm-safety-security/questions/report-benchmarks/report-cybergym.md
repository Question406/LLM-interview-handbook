---
id: report-cybergym
section: report-benchmarks
order: 7
level: S
title: "CyberGym：为什么曾经常见，而最新报告开始换掉它？"
quick: "我会先把 CyberGym 的任务讲准确：它用真实软件漏洞提供可验证的 capability signal。模型能复现漏洞，说明比静态问答更接近实际研究能力，但不自动意味着能把它发展成更强的 exploit。"
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
  - title: "CyberGym · benchmark / original source"
    url: "https://arxiv.org/abs/2506.02548"
    type: primary
  - title: "Grok 4.7 Model Card"
    url: "https://media.x.ai/v1/website/card4p7-3a96f40b.pdf"
    type: primary
  - title: "Grok 4.6 Model Card"
    url: "https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf"
    type: primary
  - title: "Claude Opus 4.6 System Card"
    url: "https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
---

## 题目描述

旧 Claude 与当前 Grok 报告使用 CyberGym，较新的 Claude 报告明确说已经因 saturation 退役。

需要讨论：解释 vulnerability reproduction 的价值、saturation 的意义与合理的替换策略。

## 回答思路

> **Situation：** 旧 Claude 与当前 Grok 报告使用 CyberGym，较新的 Claude 报告明确说已经因 saturation 退役。  
> **Task：** 解释 vulnerability reproduction 的价值、saturation 的意义与合理的替换策略。  
> **Approach / Why：** 保留历史 regression，同时引入更难的独立任务和不同 success levels。  
> **Result / Check：** 固定版本与有效 tasks；区分复现 crash、验证漏洞和完成 exploit。

## 可以这样回答

我会先把 CyberGym 的任务讲准确：它用真实软件漏洞提供可验证的 capability signal。模型能复现漏洞，说明比静态问答更接近实际研究能力，但不自动意味着能把它发展成更强的 exploit。

它在多份报告里有实际使用证据；同时，Claude Opus 5.5 报告明确提到因 saturation 而退役。这个变化说明 benchmark 需要随能力更新，不能只记住一个长期排行榜。

我会保留它做 regression，再增加不同难度和安全影响层级的任务。若只换了新名字、难度与原题高度相似，仍然解决不了 saturation。

## 报告实际采用证据

### CyberGym

**类别：** public real-world vulnerability benchmark。**优先级：** P0。

- [Grok 4.7 Model Card](https://media.x.ai/v1/website/card4p7-3a96f40b.pdf) · §6.1；PDF p.17 · `evaluated`。
- [Grok 4.6 Model Card](https://media.x.ai/v1/website/card-4p6-4cd2dc57.pdf) · §7.1；PDF p.29 · `evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §2.17；PDF p.28 · `evaluated`。
- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §3.3.4；PDF p.53 · `retired`。该报告明确说明 retired due to saturation

**读分数时看：** 按版本定义的 vulnerability reproduction success。

**适用范围：** Reproduce vulnerability 与 working exploit 不同；最新报告可能因 saturation 换用更难任务。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 先固定被报告使用的 release 和 evaluator，按软件与漏洞来源做分层。
- **Baselines / Controls：** 保留旧集作 regression，增加时间后移或更高 capability level 的 held-out tasks。
- **Metrics / Interpretation：** 分别报告 reproduction、verified effect、cost 和新旧集差异；给出未运行 tasks。

## 追问与容易误判的地方

本文把“退役”限定为已核对的 Claude Opus 5.5 system card；不推断其他实验室也停止使用。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
