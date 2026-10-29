---
id: sec-memory-attacker-models
section: memory
order: 19
level: S
title: "AgentPoison、MINJA、eTAMP：三种 memory poisoning 的权限假设有什么不同？"
quick: "我会先问攻击者到底能写哪里。AgentPoison 研究 poisoned memory 或 knowledge base，MINJA 更强调通过 queries 和观察输出引入恶意记录，eTAMP 则把入口放在 agent 看到的环境内容。"
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
  - title: "AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases"
    url: "https://arxiv.org/abs/2407.12784"
    type: primary
  - title: "A Practical Memory Injection Attack against LLM Agents (MINJA)"
    url: "https://arxiv.org/abs/2503.03704"
    type: primary
  - title: "Poison Once, Exploit Forever: Environment-Injected Memory Poisoning Attacks on Web Agents"
    url: "https://arxiv.org/abs/2604.02623"
    type: primary
---

## 题目描述

三篇论文都把 agent 的长期记忆当攻击面，但一篇能放入 records，一篇只能与 agent 对话，另一篇只改变网页 observation。

需要讨论：比较直接写入、query-mediated ingestion 与 environment-mediated ingestion 的条件，并提出公平对照。

## 回答思路

> **Situation：** 三篇论文都把 agent 的长期记忆当攻击面，但一篇能放入 records，一篇只能与 agent 对话，另一篇只改变网页 observation。  
> **Task：** 比较直接写入、query-mediated ingestion 与 environment-mediated ingestion 的条件，并提出公平对照。  
> **Approach / Why：** 沿 write/read lifecycle 描述 attacker access，分别度量写入、被检索与后续行为。  
> **Result / Check：** 所有条件都从相同 clean memory 起步，不能将写入失败与 retrieval defense 混算。

## 可以这样回答

我会先问攻击者到底能写哪里。AgentPoison 研究 poisoned memory 或 knowledge base，MINJA 更强调通过 queries 和观察输出引入恶意记录，eTAMP 则把入口放在 agent 看到的环境内容。

它们的共同结果是后续行为被持久状态影响，但进入 memory 的难度不同。直接写库可以研究 retrieval vulnerability，却不能替代“正常观察是否会被错误记住”这个问题。

比较时我会把 ingestion、persistence、retrieval 和 action 四个阶段分别计数；同样的最终 ASR 可能对应完全不同的系统薄弱点。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 固定 agent 与 clean memory，分别赋予 direct-record、query-only、environment-only access。
- **Baselines / Ablations：** 每个 setting 都包含不写 memory、只写 benign record、poisoned record 三种对照。
- **Metrics 与判读：** 报告 ingestion success、survival、retrieval exposure、downstream violation，以及每种 access 的预算。

## 追问与容易误判的地方

不允许把实验员手工插入的记录描述成攻击者在实际环境中自然诱导的写入。

## 论文依据与适用范围

- [AgentPoison: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases](https://arxiv.org/abs/2407.12784) · 2024 · research paper。
- [A Practical Memory Injection Attack against LLM Agents (MINJA)](https://arxiv.org/abs/2503.03704) · 2025 · research paper。
- [Poison Once, Exploit Forever: Environment-Injected Memory Poisoning Attacks on Web Agents](https://arxiv.org/abs/2604.02623) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
