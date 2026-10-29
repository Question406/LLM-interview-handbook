---
id: sec-proposal-security-preference-data
section: projects
order: 53
level: S
title: "Research proposal：怎样构造 agent-security preference pairs，避免学成全拒绝？"
quick: "我会先改 chosen 的定义：原任务可以安全完成时，chosen 应该是完成原任务并忽略恶意目标，而不是一句“我不能帮你”。否则 preference model 很容易学到少做事最安全。"
companies: []
tags:
  - "Safety / Security Research"
  - "Agentic Security"
  - "研究前沿 2026-10-28"
  - "2026 Research"
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: "SecAlign: Defending Against Prompt Injection with Preference Optimization"
    url: "https://arxiv.org/abs/2410.05451"
    type: primary
  - title: "Improving instruction hierarchy in frontier LLMs"
    url: "https://openai.com/index/instruction-hierarchy-challenge/"
    type: primary
  - title: "XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models"
    url: "https://arxiv.org/abs/2308.01263"
    type: primary
---

## 题目描述

团队希望用 preference optimization 改善 agent 安全性，但 rejected responses 都是明显违规，chosen responses 常常只是拒绝。

需要讨论：构建能训练 safe completion 而非 refusal shortcut 的 preference dataset，并提出验证。

## 回答思路

> **Situation：** 团队希望用 preference optimization 改善 agent 安全性，但 rejected responses 都是明显违规，chosen responses 常常只是拒绝。  
> **Task：** 构建能训练 safe completion 而非 refusal shortcut 的 preference dataset，并提出验证。  
> **Approach / Why：** 同一 injected task 下优先选择完成原任务且守规的 trajectory，控制长度、语气和任务难度。  
> **Result / Check：** 检查 held-out safe completion、over-refusal 与 reward 的 nuisance correlations。

## 可以这样回答

我会先改 chosen 的定义：原任务可以安全完成时，chosen 应该是完成原任务并忽略恶意目标，而不是一句“我不能帮你”。否则 preference model 很容易学到少做事最安全。

Pairs 最好来自同一个 task 和环境状态，清楚记录哪个 action 违规。再匹配长度、礼貌程度、格式和工具调用数量，避免模型靠这些表面差异区分。

训练后不只看 preference accuracy。我会测试新的 attacks、正常有用 instructions，以及更换 harness 后的表现；如果只是 refusal 多了，就没有证明学到了授权关系。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构造 safe completion、unsafe completion、safe failure、unsafe failure 四类 trajectories，并保留自动 state labels。
- **Baselines / Ablations：** 比较 refusal-heavy pairs、matched safe-completion pairs、instruction-priority data 与相同预算的组合。
- **Metrics 与判读：** 报告 pairwise accuracy、held-out safe completion、ASR、benign refusal 与 length/style/resource-ID nuisance tests。

## 追问与容易误判的地方

Tie 或两个都不合法的 trajectories 不适合强行标严格偏好；需要 separate labels 或多目标训练策略。

## 论文依据与适用范围

- [SecAlign: Defending Against Prompt Injection with Preference Optimization](https://arxiv.org/abs/2410.05451) · 2024 · research paper。
- [Improving instruction hierarchy in frontier LLMs](https://openai.com/index/instruction-hierarchy-challenge/) · 2026 · official research report。
- [XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models](https://arxiv.org/abs/2308.01263) · 2023 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
