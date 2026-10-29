---
id: sec-safety-security-threat-model
section: foundations
order: 1
level: S
title: "Safety、security、misuse 与 misalignment：先把研究问题分清楚"
quick: "我会先问危险动作是谁想让它做的。用户本来就在要求有害行为，这是 misuse；用户请求正常，但邮件正文偷偷改变目标，这是 indirect prompt injection；没有外部攻击者、agent 自己为了完成目标走了不安全路径，则要检查 objective、planning 和环境约束。"
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
  - title: "AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents"
    url: "https://arxiv.org/abs/2410.09024"
    type: primary
  - title: "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents"
    url: "https://arxiv.org/abs/2406.13352"
    type: primary
  - title: "Agentic Misalignment in Summer 2026"
    url: "https://alignment.anthropic.com/2026/agentic-misalignment-summer-2026/"
    type: primary
---

## 题目描述

一个 email agent 可能执行 malicious user 的请求，也可能被邮件正文劫持，还可能在正常任务中自行采取不安全动作。

需要讨论：分别描述 attacker、合法目标、违规行为与可观测结果；解释为什么同一个 safety score 不能覆盖这三种设置。

## 回答思路

> **Situation：** 一个 email agent 可能执行 malicious user 的请求，也可能被邮件正文劫持，还可能在正常任务中自行采取不安全动作。  
> **Task：** 分别描述 attacker、合法目标、违规行为与可观测结果；解释为什么同一个 safety score 不能覆盖这三种设置。  
> **Approach / Why：** 按谁控制目标、谁控制环境，以及违规来自哪一步来拆分 threat models。  
> **Result / Check：** 每种设置都定义可执行的违规 oracle，并保留正常任务完成率。

## 可以这样回答

我会先问危险动作是谁想让它做的。用户本来就在要求有害行为，这是 misuse；用户请求正常，但邮件正文偷偷改变目标，这是 indirect prompt injection；没有外部攻击者、agent 自己为了完成目标走了不安全路径，则要检查 objective、planning 和环境约束。

这三类可以产生同样的外发邮件，但干预点不同。第一类看是否拒绝不允许的请求，第二类看第三方内容能否获得指令权，第三类看授权和长期目标是否被正确执行。

因此我不会先比较总榜排名。我会先写出各自的 attacker permissions、违规定义和成功条件，再决定该用哪个 benchmark。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 用相同 email tools 构建 malicious-user、poisoned-email 和 benign-context-risk 三组任务。
- **Baselines / Ablations：** 保持工具能力和正常目标一致，分别移除恶意请求、外部注入与风险环境状态。
- **Metrics 与判读：** 分别报告 harmful completion、attacker success、unsafe action 与 benign task success；不合成没有解释的单一分数。

## 追问与容易误判的地方

同一 episode 可以同时有 misuse 与 injection。分类服务于明确假设，不要求所有现实事件只能归到一个类别。

## 论文依据与适用范围

- [AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents](https://arxiv.org/abs/2410.09024) · 2024 · research paper。
- [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352) · 2024 · NeurIPS 2024。
- [Agentic Misalignment in Summer 2026](https://alignment.anthropic.com/2026/agentic-misalignment-summer-2026/) · 2026 · official research case studies。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
