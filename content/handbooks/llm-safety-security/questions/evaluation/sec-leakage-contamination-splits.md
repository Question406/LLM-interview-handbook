---
id: sec-leakage-contamination-splits
section: evaluation
order: 40
level: A
title: "Safety benchmark 也会 contamination：怎样做 family-level 与 environment-level splits？"
quick: "我会把近重复和机制重复分开。文本没有重合，不代表模型没见过同一种“伪装成管理员要求”的套路；反过来，完全新环境也可能因为工具太难而让所有攻击都失败。"
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
  - title: "HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal"
    url: "https://arxiv.org/abs/2402.04249"
    type: primary
  - title: "Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks"
    url: "https://arxiv.org/abs/2602.20156"
    type: primary
---

## 题目描述

攻击模板、skill 文件与 judge rubrics 都公开了，后续训练很可能见过其中的文字和改写。

需要讨论：设计能检验未知攻击机制与新环境迁移的数据划分，解释可复现与隐藏测试的取舍。

## 回答思路

> **Situation：** 攻击模板、skill 文件与 judge rubrics 都公开了，后续训练很可能见过其中的文字和改写。  
> **Task：** 设计能检验未知攻击机制与新环境迁移的数据划分，解释可复现与隐藏测试的取舍。  
> **Approach / Why：** 在模板、来源、语义目标和环境多个层级做 deduplication 与 held-out splits。  
> **Result / Check：** 同时报告 public regression、fresh hidden test 与跨环境表现，不用一个随机 split 代表全部。

## 可以这样回答

我会把近重复和机制重复分开。文本没有重合，不代表模型没见过同一种“伪装成管理员要求”的套路；反过来，完全新环境也可能因为工具太难而让所有攻击都失败。

数据应记录 attack family、source lineage、目标行为、tool schema 和 environment，再按这些单位划分。可以保留公开集做 regression，另外持续生成未发布的任务做 fresh evaluation。

隐藏集不是永远不公开。一个实用做法是定期冻结、退役再发布，让复现与持续防止过拟合都能进行。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 对 attacks、skills、tasks 与 rubrics 建立 lineage，先去近重复，再做 template/domain/tool-schema 留出。
- **Baselines / Ablations：** 对比 random split、family split、environment split 和时间后移的 fresh split。
- **Metrics 与判读：** 报告各 split 的 clean capability、ASR、safe completion，以及近重复与跨来源污染审计。

## 追问与容易误判的地方

“模型没见过”通常无法完全证明；应说明训练信息可见性、去重方法与剩余不确定性。

## 论文依据与适用范围

- [HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal](https://arxiv.org/abs/2402.04249) · 2024 · research paper。
- [Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks](https://arxiv.org/abs/2602.20156) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
