---
id: report-gray-swan-ipi
section: report-benchmarks
order: 2
level: S
title: "Gray Swan IPI / ART：frontier reports 怎样测多次尝试后的 injection risk？"
quick: "这应该是优先读的 agent-security benchmark。它把攻击放在 agent 读取外部内容的过程中，并在报告里明确区分尝试预算。看到 k=15 的数字，我会先解释它是攻击者在一定预算内找到成功攻击的概率，不是单次调用的失败概率。"
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
  - title: "Gray Swan IPI / historical ART · benchmark / original source"
    url: "https://arxiv.org/abs/2603.15714"
    type: primary
  - title: "Claude Opus 5.5 System Card"
    url: "https://www.anthropic.com/claude-opus-5-5-system-card"
    type: primary
  - title: "Gemini 4 Argon Safety & Security Report"
    url: "https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf"
    type: primary
  - title: "Claude Opus 4.6 System Card"
    url: "https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf"
    type: primary
---

## 题目描述

Claude 和 Gemini 的近期报告都展示了 Gray Swan IPI，但旧 Claude 报告还使用 ART 名称。

需要讨论：解释攻击从哪里进入、k attempts 的含义，以及为什么版本、fallback 与 safeguards 必须一起记录。

## 回答思路

> **Situation：** Claude 和 Gemini 的近期报告都展示了 Gray Swan IPI，但旧 Claude 报告还使用 ART 名称。  
> **Task：** 解释攻击从哪里进入、k attempts 的含义，以及为什么版本、fallback 与 safeguards 必须一起记录。  
> **Approach / Why：** 按 release、surface 与 endpoint 对齐，再比较 cumulative attack success。  
> **Result / Check：** 正常任务完成率、单次成功与预算内成功同时报告。

## 可以这样回答

这应该是优先读的 agent-security benchmark。它把攻击放在 agent 读取外部内容的过程中，并在报告里明确区分尝试预算。看到 k=15 的数字，我会先解释它是攻击者在一定预算内找到成功攻击的概率，不是单次调用的失败概率。

我也会核对是否启用了 blocking classifiers、发生 fallback 时实际用了哪个模型，以及 coding、tool use、GUI cases 是否都参与了平均。ART 和后续 IPI 不能只凭名字相近就拼成一条历史曲线。

自己的实验会补 safe completion：攻击没成功，但 agent 完全放弃原任务，不是理想结果。

## 报告实际采用证据

### Gray Swan IPI / historical ART

**类别：** external benchmark / competition-derived replay。**优先级：** P0。

- [Claude Opus 5.5 System Card](https://www.anthropic.com/claude-opus-5-5-system-card) · §5.2.1；PDF pp.84–85 · `external_evaluated`。
- [Gemini 4 Argon Safety & Security Report](https://storage.googleapis.com/deepmind-media/gemini/gemini_4_safety_report.pdf) · §6.1.2.6 / Figure 6.9；PDF pp.211–212 · `external_evaluated`。
- [Claude Opus 4.6 System Card](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf) · §5.2.1；PDF pp.83–84 · `external_evaluated`。历史名称 ART；与当前 IPI 分开

**读分数时看：** Attack success within k attempts；固定 Q1/Q2、场景集、model endpoint 与 safeguards。

**适用范围：** ART 与后续 IPI 的版本、surface 与 k 可能改变，不能直接合并历史 scores。

## 研究实验怎么设计

以下是手册提出的复现或扩展方案。

- **Setting：** 固定某一版 scenarios、攻击集与 k，保存 tool/browser/coding 三类 outcomes。
- **Baselines / Controls：** 对比 clean、attack、同预算 repeated trials；明确 static replay 与 adaptive search。
- **Metrics / Interpretation：** 报告 success@k、safe completion、各 surface 结果、actual fallback model 与有效样本数。

## 追问与容易误判的地方

不要从单次 ASR 直接用独立假设推导真实 adaptive attack@k；不同 attempts 往往相关。

原始 benchmark、报告中的实际 variant 与本卡提出的实验分开记录。核对截止：2026-10-28。
