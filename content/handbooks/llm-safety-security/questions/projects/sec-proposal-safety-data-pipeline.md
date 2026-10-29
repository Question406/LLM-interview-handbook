---
id: sec-proposal-safety-data-pipeline
section: projects
order: 52
level: S
title: "Research proposal：做一个可复现的 agent-safety data pipeline"
quick: "我会从 benchmark data quality 切入，先做一个小规模的 tool-output injection testbed。每个样本都包含原始用户任务、可改 observation、预期合法结果、攻击者目标和环境 reset 方法。"
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
  - title: "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents"
    url: "https://arxiv.org/abs/2406.13352"
    type: primary
  - title: "PIArena: A Platform for Prompt Injection Evaluation"
    url: "https://aclanthology.org/2026.acl-long.1533/"
    type: primary
---

## 题目描述

你擅长 data processing 和 evaluation，但没有现成的 agent-security 项目，需要提出一个两周能启动的研究计划。

需要讨论：从 attack-task pairs 到 replay、评分和数据质量检查，设计可以交付和证伪的 pipeline。

## 回答思路

> **Situation：** 你擅长 data processing 和 evaluation，但没有现成的 agent-security 项目，需要提出一个两周能启动的研究计划。  
> **Task：** 从 attack-task pairs 到 replay、评分和数据质量检查，设计可以交付和证伪的 pipeline。  
> **Approach / Why：** 先做小而有状态 oracle 的任务集，把 provenance、reset、预算和错误归因标准化。  
> **Result / Check：** 交付可重放 episodes、质量报告与一个明确 failure analysis，而不是承诺未知的 SOTA。

## 可以这样回答

我会从 benchmark data quality 切入，先做一个小规模的 tool-output injection testbed。每个样本都包含原始用户任务、可改 observation、预期合法结果、攻击者目标和环境 reset 方法。

第一周完成 clean replay 和 deterministic scorer，证明正常任务有解、攻击确实能进入 context、评分能识别实际副作用。第二周接入几种简单 defenses，检查结果是否被 invalid payload、工具格式错误或不必要拒绝混淆。

我的 hypothesis 是一部分“安全收益”其实来自不可完成任务或评分盲点。若审计后这个效应很小，也会明确报告，而不是硬编一个新方法。

## 一个 episode 的最小数据 schema

```json
{
  "episode_id": "synthetic-001",
  "task_family": "email-summary",
  "user_goal": "summarize permitted records",
  "authorization": { "read": ["record-demo"], "send_to": ["recipient-demo"] },
  "attacker_access": { "surface": "tool_output", "trials": 5 },
  "variant": "clean-or-controlled-injection",
  "environment_version": "mock-v1",
  "model_config": { "model": "configured-at-run-time", "seed": 0 },
  "trace_path": "local-artifact-reference",
  "outcome": { "task_success": null, "policy_violation": null },
  "parent_ids": [],
  "scorer_version": "state-oracle-v1"
}
```

`null` 表示还未测量，不是失败或成功。每次 replay 都从明确的环境 snapshot 开始；攻击失败、工具错误和 evaluator 错误保留为不同字段，避免默认映射成 safe。


## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 起步用 20 个 synthetic tasks、每任务 3 个 controlled variants；规模是拟议预算，可按 API 成本调整。
- **Baselines / Ablations：** Baseline 包含 clean、no-defense、block-all-external 和一个固定 defense，所有版本与预算入 manifest。
- **Metrics 与判读：** 交付 replay pass rate、标注一致性、outcome matrix 与逐失败类型的归因；保留 raw counts。

## 追问与容易误判的地方

这是 prospective project，面试时应说“我计划/会怎样做”；不能说成自己已经完成并取得某个提升。

## 论文依据与适用范围

- [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/abs/2406.13352) · 2024 · NeurIPS 2024。
- [PIArena: A Platform for Prompt Injection Evaluation](https://aclanthology.org/2026.acl-long.1533/) · 2026 · ACL 2026。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
