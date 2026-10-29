---
id: sec-multiagent-monitor-collusion
section: alignment
order: 47
level: A
title: "多个 agents 互相监督，会自动更安全吗？"
quick: "我不会把“三个 agents 都说安全”直接当成三份独立证据。它们可能用同一底座、同样 prompt，也读到同一个被污染的摘要，自然会一起犯错。"
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
  - title: "Evaluating Control Protocols for Untrusted AI Agents"
    url: "https://arxiv.org/abs/2511.02997"
    type: primary
  - title: "Agent Smith: A Single Image Can Jailbreak One Million Multimodal LLM Agents Exponentially Fast"
    url: "https://arxiv.org/abs/2402.08567"
    type: primary
---

## 题目描述

系统让同一模型分别扮演 actor、reviewer 与 planner，希望通过互相检查降低错误和风险。

需要讨论：分析 correlated failure、信息隔离与可能的 coordination，提出有解释力的对照。

## 回答思路

> **Situation：** 系统让同一模型分别扮演 actor、reviewer 与 planner，希望通过互相检查降低错误和风险。  
> **Task：** 分析 correlated failure、信息隔离与可能的 coordination，提出有解释力的对照。  
> **Approach / Why：** 分别改变模型来源、可见信息、communication 与权限，避免把多次同类判断当独立证据。  
> **Result / Check：** 在总预算匹配下测联合失败，保留 reviewer disagreement 与真实 outcomes。

## 可以这样回答

我不会把“三个 agents 都说安全”直接当成三份独立证据。它们可能用同一底座、同样 prompt，也读到同一个被污染的摘要，自然会一起犯错。

实验应分开测试 diversity 和 isolation 的贡献：更换 reviewer 模型、隐藏 actor 的自我辩护、给 reviewer 独立的 action/state log，再限制它能否直接执行。

如果要讨论 collusion，就需要特定的可验证协调行为；一般的同错可以先用 correlated errors 解释。对比时总 token 和 latency 也要匹配，否则更多计算本身会带来收益。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构建 actor/reviewer workflows，分别设置同模型/异模型、共享/独立 observations、有/无 communication。
- **Baselines / Ablations：** 加入同预算单模型复查、随机审计和 deterministic policy checker。
- **Metrics 与判读：** 报告 joint false-negative rate、错误相关性、safe completion、cost 和独立证据是否真的增加。

## 追问与容易误判的地方

Disagreement 不等于可靠 uncertainty；几个模型都看不到真实 resource state 时，一致与分歧都可能没有安全意义。

## 论文依据与适用范围

- [Evaluating Control Protocols for Untrusted AI Agents](https://arxiv.org/abs/2511.02997) · 2025 · research paper。
- [Agent Smith: A Single Image Can Jailbreak One Million Multimodal LLM Agents Exponentially Fast](https://arxiv.org/abs/2402.08567) · 2024 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
