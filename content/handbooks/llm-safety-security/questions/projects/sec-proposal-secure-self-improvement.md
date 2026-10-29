---
id: sec-proposal-secure-self-improvement
section: projects
order: 56
level: S
title: "Research proposal：data flywheel 怎样避免把攻击轨迹当“成功经验”？"
quick: "我会先把成功定义改成 safe completion。任务完成但夹带越权步骤的 trajectory，不该因为答案正确就进入“好经验”池。"
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
  - title: "MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Experience Retrieval"
    url: "https://arxiv.org/abs/2512.16962"
    type: primary
  - title: "Poison Once, Exploit Forever: Environment-Injected Memory Poisoning Attacks on Web Agents"
    url: "https://arxiv.org/abs/2604.02623"
    type: primary
  - title: "SecAlign: Defending Against Prompt Injection with Preference Optimization"
    url: "https://arxiv.org/abs/2410.05451"
    type: primary
---

## 题目描述

Agent 自动收集完成任务的 trajectories，用于经验检索、synthetic demonstrations 和下一轮训练。

需要讨论：设计 quality/safety filters、provenance、selection criteria 与跨迭代的污染测量。

## 回答思路

> **Situation：** Agent 自动收集完成任务的 trajectories，用于经验检索、synthetic demonstrations 和下一轮训练。  
> **Task：** 设计 quality/safety filters、provenance、selection criteria 与跨迭代的污染测量。  
> **Approach / Why：** 只有 task success 与 policy checks 都通过才进入候选池；下游派生样本保留 lineage，并用 fresh tests 评估。  
> **Result / Check：** 逐轮报告 contamination amplification、utility gain 和新攻击泛化，不只看训练集奖励。

## 可以这样回答

我会先把成功定义改成 safe completion。任务完成但夹带越权步骤的 trajectory，不该因为答案正确就进入“好经验”池。

进入候选池后，记录原始环境、授权与来源，再检查 synthetic generator 有没有把某次特定许可推广成通用流程。派生数据要保留父样本关系，方便污染发生后追踪和回滚。

实验可以故意在候选池中放少量受控污染，观察经过检索、生成和训练几个环节后是被稀释还是放大。即使任务分上涨，也要看 fresh adversarial tests 是否变差。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 使用 sandbox trajectories 和少量带标记的 poisoned seeds，模拟 retrieval→generation→selection 的多轮迭代。
- **Baselines / Ablations：** 比较 outcome-only selection、policy-aware selection、lineage-aware rollback 与无 self-improvement。
- **Metrics 与判读：** 测污染 lineage 的扩增比例、safe utility、unseen attack success 和恢复代价；各轮测试集隔离。

## 追问与容易误判的地方

这里只是研究设计。若不实际做参数训练，结果应称为经验库或示例选择的迭代实验，不称为 post-training 收益。

## 论文依据与适用范围

- [MemoryGraft: Persistent Compromise of LLM Agents via Poisoned Experience Retrieval](https://arxiv.org/abs/2512.16962) · 2025 · preprint。
- [Poison Once, Exploit Forever: Environment-Injected Memory Poisoning Attacks on Web Agents](https://arxiv.org/abs/2604.02623) · 2026 · preprint。
- [SecAlign: Defending Against Prompt Injection with Preference Optimization](https://arxiv.org/abs/2410.05451) · 2024 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
