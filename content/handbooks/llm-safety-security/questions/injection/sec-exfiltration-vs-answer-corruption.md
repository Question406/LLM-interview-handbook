---
id: sec-exfiltration-vs-answer-corruption
section: injection
order: 11
level: A
title: "Answer corruption 与 data exfiltration 为什么需要不同的 success oracles？"
quick: "我会把“说错了什么”和“多透露了什么”拆开。Answer corruption 可以通过价格、事实或来源是否错误来判断；泄露则要检查有谁获得了本不该拿到的信息，即使最终答案完全正确也会失败。"
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
  - title: "PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models"
    url: "https://arxiv.org/abs/2402.07867"
    type: primary
  - title: "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents"
    url: "https://arxiv.org/abs/2403.02691"
    type: primary
---

## 题目描述

攻击者让 agent 给出错误价格；另一种攻击让 agent 仍给正确价格，却额外发送了 synthetic confidential record。

需要讨论：分别定义 integrity 与 confidentiality failures，解释 reference-answer matching 的盲点。

## 回答思路

> **Situation：** 攻击者让 agent 给出错误价格；另一种攻击让 agent 仍给正确价格，却额外发送了 synthetic confidential record。  
> **Task：** 分别定义 integrity 与 confidentiality failures，解释 reference-answer matching 的盲点。  
> **Approach / Why：** 用 answer correctness 评估内容，用独立 sink/event evaluator 检查信息是否越过授权范围。  
> **Result / Check：** 先做可验证的 exact outcomes，再补 semantic leakage；不能靠 judge 一次打分包办。

## 可以这样回答

我会把“说错了什么”和“多透露了什么”拆开。Answer corruption 可以通过价格、事实或来源是否错误来判断；泄露则要检查有谁获得了本不该拿到的信息，即使最终答案完全正确也会失败。

Synthetic secrets 很适合建立第一版 oracle：每个 episode 生成新的随机 token，工具只写到隔离的 mock sink。这样能可靠判断实际发生的流转。

之后再加 paraphrase、partial disclosure 和推断性泄露，因为 exact match 只覆盖最容易测的一部分；两类结果会分别报告。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 同一 benign task 配置独立 integrity target 与 confidentiality target，所有 records 使用 synthetic data。
- **Baselines / Ablations：** 对比 final-answer-only judge、tool-event evaluator 和联合 evaluator；加入部分泄露 cases。
- **Metrics 与判读：** 分别报告 targeted wrong answer、unauthorized recipient exposure、partial leakage 和正常任务完成。

## 追问与容易误判的地方

系统 prompt 被复述不必然等同高严重度泄露；要事先明确哪些信息被视为 secret、实际影响是什么。

## 论文依据与适用范围

- [PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models](https://arxiv.org/abs/2402.07867) · 2024 · research paper。
- [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents](https://arxiv.org/abs/2403.02691) · 2024 · Findings of ACL 2024。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
