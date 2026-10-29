---
id: sec-multiagent-infection-delegation
section: multimodal
order: 27
level: A
title: "Agent Smith 到 multi-agent delegation：传播攻击该怎么测？"
quick: "我会先追究接收方为什么信任 worker 的摘要。Agent 是内部组件，不意味着它转述的网页内容就变成高权限指令。尤其在 delegation 时，消息必须说明谁授权了什么，而不只是“另一个 agent 要我这样做”。"
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
  - title: "Agent Smith: A Single Image Can Jailbreak One Million Multimodal LLM Agents Exponentially Fast"
    url: "https://arxiv.org/abs/2402.08567"
    type: primary
  - title: "The Blind Spot of Agent Safety: How Benign User Instructions Expose Critical Vulnerabilities in Computer-Use Agents"
    url: "https://arxiv.org/abs/2604.10577"
    type: primary
---

## 题目描述

一个 worker 读到不可信内容后把摘要发给其他 workers；接收方可能把同事的消息当成可信指令。

需要讨论：区分内容传播、指令采纳与实际越权，设计可测的 multi-agent security experiment。

## 回答思路

> **Situation：** 一个 worker 读到不可信内容后把摘要发给其他 workers；接收方可能把同事的消息当成可信指令。  
> **Task：** 区分内容传播、指令采纳与实际越权，设计可测的 multi-agent security experiment。  
> **Approach / Why：** 按 agent identity 与 message provenance 传播信任属性，限制每次 delegation 的有效权限。  
> **Result / Check：** 报告传播范围与成功副作用，控制拓扑、共享 memory 和总体能力。

## 可以这样回答

我会先追究接收方为什么信任 worker 的摘要。Agent 是内部组件，不意味着它转述的网页内容就变成高权限指令。尤其在 delegation 时，消息必须说明谁授权了什么，而不只是“另一个 agent 要我这样做”。

Agent Smith 的大规模模拟提供了传播风险的 proof of concept，但现实团队的 topology、模型和权限差别很大。我会从可复现的小规模 workflow 开始，逐步改变共享状态和交互方式。

要区分“恶意文本被转发了”与“其他 agents 真的做了越权动作”，否则传播速度指标会夸大风险。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构建 2/4/8-worker mock teams，操纵 graph topology、shared memory 和 message source labels。
- **Baselines / Ablations：** 比较共享全部权限、每 worker scope、delegation-specific capabilities 和 taint-preserving messages。
- **Metrics 与判读：** 测 exposure/adoption/execution 的传播曲线、受影响资源、team task success 与总 token 成本。

## 追问与容易误判的地方

规模增大时需要匹配总预算。更多 agents 的更高违规率，可能来自更多调用而非特殊的传播机制。

## 论文依据与适用范围

- [Agent Smith: A Single Image Can Jailbreak One Million Multimodal LLM Agents Exponentially Fast](https://arxiv.org/abs/2402.08567) · 2024 · research paper。
- [The Blind Spot of Agent Safety: How Benign User Instructions Expose Critical Vulnerabilities in Computer-Use Agents](https://arxiv.org/abs/2604.10577) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
