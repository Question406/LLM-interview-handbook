---
id: sec-adaptive-tool-chain-attacks
section: injection
order: 10
level: A
title: "Tool chaining 与 objective drift：每一步都看似合理，为什么整段 trajectory 会违规？"
quick: "我会先保留用户原始目标，避免后面的 intermediate plan 被当成新的授权。单看“读取文件”或“同步报告”都可能正常，但组合起来可能把任务外的数据带到错误位置。"
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
  - title: "AgentLAB: Benchmarking LLM Agents against Long-Horizon Attacks"
    url: "https://arxiv.org/abs/2602.16901"
    type: primary
---

## 题目描述

一个正常资料整理任务逐渐变成读取更多文件、生成额外报告，最后把报告同步到任务外的位置。

需要讨论：解释 long-horizon attack 怎样利用中间目标，并提出 trajectory-level 检测方法。

## 回答思路

> **Situation：** 一个正常资料整理任务逐渐变成读取更多文件、生成额外报告，最后把报告同步到任务外的位置。  
> **Task：** 解释 long-horizon attack 怎样利用中间目标，并提出 trajectory-level 检测方法。  
> **Approach / Why：** 跟踪原始目标、授权资源与 action dependencies，检查组合结果是否扩大目的或数据范围。  
> **Result / Check：** 在相同步数和任务难度下评估整段违规，而不只分类单个 tool call。

## 可以这样回答

我会先保留用户原始目标，避免后面的 intermediate plan 被当成新的授权。单看“读取文件”或“同步报告”都可能正常，但组合起来可能把任务外的数据带到错误位置。

需要记录每个 action 是为哪个用户目标服务、参数来自哪里，以及是否新引入了一个用户没要求的 destination。Runtime 能限制资源与目的地，trajectory monitor 则检查任务范围是否逐步扩大。

实验不能只拿长任务和短任务比，因为长任务本来就更难。我会匹配 action 数与基础成功率，再操纵攻击需要多少中间步骤。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构造 1/3/6 次依赖步骤后才显现违规目标的 sandbox workflows。
- **Baselines / Ablations：** 比较 per-message detector、per-action checker、trajectory monitor 与 original-goal-aware checker。
- **Metrics 与判读：** 报告 task-level ASR、违规前 lead time、误报、safe completion 与每步额外开销。

## 追问与容易误判的地方

只把累计风险上升归因于“模型容易被说服”太早；先检查是不是接触面增加或原始授权在 compaction 中丢失。

## 论文依据与适用范围

- [AgentLAB: Benchmarking LLM Agents against Long-Horizon Attacks](https://arxiv.org/abs/2602.16901) · 2026 · ICML 2026。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
