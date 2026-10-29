---
id: sec-proposal-skill-permission-generalization
section: projects
order: 54
level: S
title: "Research proposal：把 skill security 做成 permission generalization 问题"
quick: "我想研究的不是“这句话像不像恶意”，而是 agent 能不能判断这个动作是否被当前任务授权。比如同样的写文件要求，在明确授权整理目录时合理，在只读摘要任务中就不合理。"
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
  - title: "Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks"
    url: "https://arxiv.org/abs/2602.20156"
    type: primary
  - title: "SkillGuard: A Permission-Centric Framework for Agent Skill Security"
    url: "https://arxiv.org/abs/2606.03024"
    type: primary
---

## 题目描述

新 skill、新 tool 名字不断出现，训练集不可能枚举所有可疑措辞。

需要讨论：提出检验模型是否理解 action/resource/authorization 关系的数据与实验，而不是只识别攻击模板。

## 回答思路

> **Situation：** 新 skill、新 tool 名字不断出现，训练集不可能枚举所有可疑措辞。  
> **Task：** 提出检验模型是否理解 action/resource/authorization 关系的数据与实验，而不是只识别攻击模板。  
> **Approach / Why：** 用相同任务做权限与来源 counterfactuals，留出完整 skill families 和 tool schemas。  
> **Result / Check：** 如果模型仅换名称就失败，要归因到表面模式；runtime violation 与语言判断分别测。

## 可以这样回答

我想研究的不是“这句话像不像恶意”，而是 agent 能不能判断这个动作是否被当前任务授权。比如同样的写文件要求，在明确授权整理目录时合理，在只读摘要任务中就不合理。

数据可以固定 action，只改变用户授权、resource scope 或来源；也可以固定授权关系，改写文案和 tool 名称。这样能分离语义理解与模板识别。

第一版用 mock files 和 synthetic users，先把 labels 做得可验证。结果即使发现模型没有明显 generalization，也能为 runtime permissions 提供有针对性的 failure slices。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构造 task × skill × permission 的 counterfactual grid，合法/非法 pairs 尽量只改一个因素。
- **Baselines / Ablations：** 比较 lexical detector、context-aware model、manifest matcher 和 actual policy executor。
- **Metrics 与判读：** 测 unseen skill/schema 的 authorization accuracy、safe completion、实际越权与 counterfactual consistency。

## 追问与容易误判的地方

Counterfactual 变化必须真的改变授权标签；仅改变公司名或人名不应无故改变决策。

## 论文依据与适用范围

- [Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks](https://arxiv.org/abs/2602.20156) · 2026 · preprint。
- [SkillGuard: A Permission-Centric Framework for Agent Skill Security](https://arxiv.org/abs/2606.03024) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
