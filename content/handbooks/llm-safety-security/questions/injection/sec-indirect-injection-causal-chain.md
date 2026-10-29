---
id: sec-indirect-injection-causal-chain
section: injection
order: 7
level: S
title: "Indirect prompt injection：如何定位从 untrusted text 到 side effect 的因果链？"
quick: "我会沿着来源到动作追：网页是否实际进入 context，agent 是否采纳了其中的目标，是否生成了对应 tool call，executor 有没有执行，以及外部状态到底变了什么。"
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
  - title: "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents"
    url: "https://arxiv.org/abs/2403.02691"
    type: primary
  - title: "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents"
    url: "https://arxiv.org/abs/2406.13352"
    type: primary
---

## 题目描述

研究 assistant 读取一个网页后，多调用了一次原任务不需要的外发工具。最终答案看起来仍然正确。

需要讨论：说明要保存哪些 trace，如何判断恶意指令真正影响了行为，而不是事后相关。

## 回答思路

> **Situation：** 研究 assistant 读取一个网页后，多调用了一次原任务不需要的外发工具。最终答案看起来仍然正确。  
> **Task：** 说明要保存哪些 trace，如何判断恶意指令真正影响了行为，而不是事后相关。  
> **Approach / Why：** 对相同任务做 clean / injected paired runs，再检查 instruction adoption、tool arguments 和环境变化。  
> **Result / Check：** 分别测到达、采纳、尝试执行与真正成功，保留完成正常任务的结果。

## 可以这样回答

我会沿着来源到动作追：网页是否实际进入 context，agent 是否采纳了其中的目标，是否生成了对应 tool call，executor 有没有执行，以及外部状态到底变了什么。

只看最终回答很容易漏掉“任务完成了，同时做了额外坏事”。也不能看到一次外发就直接归因于 payload，要用相同任务的 clean run 和去掉攻击段的版本作对照。

如果能固定工具返回、模型配置和 seed，就先做 paired comparison；对 sampling 的不确定性再重复多个 runs。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 在 mock tools 中放 synthetic records 和 inert external sink，保存 observation/action/state logs。
- **Baselines / Ablations：** 比较 clean、只加等长无害文本、含攻击意图的修改三种 tool responses。
- **Metrics 与判读：** 分阶段报告 exposed/adopted/attempted/executed/attacker-success，并检查 benign task completion。

## 追问与容易误判的地方

Attempted violation 与 prevented violation 都有研究价值。Executor 挡住后不能说模型从未受影响，也不能算实际泄露。

## 论文依据与适用范围

- [InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents](https://arxiv.org/abs/2403.02691) · 2024 · Findings of ACL 2024。
- [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352) · 2024 · NeurIPS 2024。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
