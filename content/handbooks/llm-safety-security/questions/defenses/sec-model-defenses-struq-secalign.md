---
id: sec-model-defenses-struq-secalign
section: defenses
order: 32
level: S
title: "StruQ、Instruction Hierarchy 与 SecAlign：model-level defenses 如何比较？"
quick: "我会先看每个方法希望模型学到什么。StruQ 把 instruction 与 data 分开并配合专门训练；Instruction Hierarchy 教模型在指令冲突时按优先级处理；SecAlign 用 secure 与 insecure responses 的偏好信号拉开差距。"
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
  - title: "StruQ: Defending Against Prompt Injection with Structured Queries"
    url: "https://arxiv.org/abs/2402.06363"
    type: primary
  - title: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions"
    url: "https://arxiv.org/abs/2404.13208"
    type: primary
  - title: "SecAlign: Defending Against Prompt Injection with Preference Optimization"
    url: "https://arxiv.org/abs/2410.05451"
    type: primary
  - title: "Meta SecAlign: A Secure Foundation LLM Against Prompt Injection Attacks"
    url: "https://arxiv.org/abs/2507.02735"
    type: primary
---

## 题目描述

你可以调整 serialization、做 SFT 或做 preference optimization，但训练预算有限。

需要讨论：比较输入分离、priority learning 与 secure/insecure preferences 的训练信号，设计公平 ablations。

## 回答思路

> **Situation：** 你可以调整 serialization、做 SFT 或做 preference optimization，但训练预算有限。  
> **Task：** 比较输入分离、priority learning 与 secure/insecure preferences 的训练信号，设计公平 ablations。  
> **Approach / Why：** 固定 base model 与 data budget，将格式、训练目标和攻击数据分别改变。  
> **Result / Check：** 在未见 domains、attack families 与 agent harness 上测 robustness 和 utility。

## 可以这样回答

我会先看每个方法希望模型学到什么。StruQ 把 instruction 与 data 分开并配合专门训练；Instruction Hierarchy 教模型在指令冲突时按优先级处理；SecAlign 用 secure 与 insecure responses 的偏好信号拉开差距。

公平比较不能只看最后模型名，因为 base model、数据量和工具能力都可能不同。可以先用同一底座分别改变 serialization、SFT signal 和 preference objective，再看哪些收益是互补的。

Model-level defense 很有价值，但它是经验 robustness。对高影响 side effects，我仍会配合独立的 runtime authorization。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构建相同 benign tasks 与 injected inputs，secure completion 保持任务可用，insecure completion 体现具体目标偏离。
- **Baselines / Ablations：** 做 format-only、SFT-only、preference-only、组合及 equal-token training 对照。
- **Metrics 与判读：** 报告 held-out ASR、safe completion、over-refusal、tool competence 与每单位训练预算收益。

## 追问与容易误判的地方

只换 delimiters 没有专门训练，不能称作复现 StruQ；使用公开 SecAlign checkpoint 也不能隔离训练目标本身的贡献。

## 论文依据与适用范围

- [StruQ: Defending Against Prompt Injection with Structured Queries](https://arxiv.org/abs/2402.06363) · 2024 · research paper。
- [The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions](https://arxiv.org/abs/2404.13208) · 2024 · research paper。
- [SecAlign: Defending Against Prompt Injection with Preference Optimization](https://arxiv.org/abs/2410.05451) · 2024 · research paper。
- [Meta SecAlign: A Secure Foundation LLM Against Prompt Injection Attacks](https://arxiv.org/abs/2507.02735) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
