---
id: sec-ignored-not-refused-outcomes
section: evaluation
order: 37
level: S
title: "低 ASR 是真的防住了，还是 agent 根本没行动？"
quick: "我会先问这个 agent 在没有攻击时能不能做完任务。若 clean run 都不会调用工具，低 ASR 不能直接说明它懂得拒绝 injection。"
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
  - title: "Ignored, Not Refused: What Low Prompt-Injection Success Rates Hide in Small Tool-Using Agents"
    url: "https://arxiv.org/abs/2610.23254"
    type: primary
  - title: "Safety, or Just Capability? A Validity Audit of Agent-Safety Benchmarks"
    url: "https://arxiv.org/abs/2607.28685"
    type: primary
---

## 题目描述

小模型的 injection ASR 比大模型低很多，但它也经常不调用工具、忽略资料或提前停止。

需要讨论：定义能区分 refusal、ignored injection、capability failure 与 successful defense 的 outcome taxonomy。

## 回答思路

> **Situation：** 小模型的 injection ASR 比大模型低很多，但它也经常不调用工具、忽略资料或提前停止。  
> **Task：** 定义能区分 refusal、ignored injection、capability failure 与 successful defense 的 outcome taxonomy。  
> **Approach / Why：** 用 clean counterpart 与行为 trace 判断失败原因，并保留 task/safety 的联合结果。  
> **Result / Check：** 在同一模型不同 prompts 和不同能力水平下复验，不把某一 preprint 的比例直接迁移。

## 可以这样回答

我会先问这个 agent 在没有攻击时能不能做完任务。若 clean run 都不会调用工具，低 ASR 不能直接说明它懂得拒绝 injection。

Ignored, Not Refused 这篇 2026-10 preprint 的切入点，就是把失败攻击进一步拆开。我会同时记录显式拒绝、继续完成合法任务、忽略全部 context、工具格式错误和超时。

其中“没口头拒绝，但正确完成任务”也可以是好防御。真正重要的是有没有保住用户目标、有没有违规，以及结论是否被基础能力差异混淆。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 对相同 episode 运行 clean 与 attacked variants，人工复核部分 trace，再训练或校准 judge。
- **Baselines / Ablations：** 比较同模型的不同 system prompts、不同模型，以及 task-capability matched subsets。
- **Metrics 与判读：** 报告 outcome matrix、clean/attacked task success、ASR 和失败原因分布；说明 conditional subsets 的选择规则。

## 追问与容易误判的地方

不能把“不显式拒绝”一律当成不安全。Ignore injection 并完成原任务，本来就可能是理想行为。

## 论文依据与适用范围

- [Ignored, Not Refused: What Low Prompt-Injection Success Rates Hide in Small Tool-Using Agents](https://arxiv.org/abs/2610.23254) · 2026 · preprint · 2026-10。
- [Safety, or Just Capability? A Validity Audit of Agent-Safety Benchmarks](https://arxiv.org/abs/2607.28685) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
