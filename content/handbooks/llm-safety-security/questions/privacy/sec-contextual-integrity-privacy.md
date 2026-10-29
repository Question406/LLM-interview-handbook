---
id: sec-contextual-integrity-privacy
section: privacy
order: 48
level: S
title: "PrivacyLens：知道 privacy norms 与执行时保护隐私，差距在哪里？"
quick: "我会把 privacy 看成“这条信息在这个关系和目的下是否该流动”。同一个健康信息发给用户指定的医生和公开工作频道，性质不同，所以仅查有没有敏感词不够。"
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
  - title: "PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action"
    url: "https://arxiv.org/abs/2409.00138"
    type: primary
---

## 题目描述

模型在问答中能说出某类信息不应分享，但写外发邮件时仍把它当作有用背景加入。

需要讨论：按 sender、recipient、subject、information type 与 transmission purpose 建立评价。

## 回答思路

> **Situation：** 模型在问答中能说出某类信息不应分享，但写外发邮件时仍把它当作有用背景加入。  
> **Task：** 按 sender、recipient、subject、information type 与 transmission purpose 建立评价。  
> **Approach / Why：** 把同一 privacy norm 从 vignette 推进到实际 tool action，构造 recipient/purpose matched pairs。  
> **Result / Check：** 判定实际传递而非只测 privacy 常识，并检查正常信息传递是否保留。

## 可以这样回答

我会把 privacy 看成“这条信息在这个关系和目的下是否该流动”。同一个健康信息发给用户指定的医生和公开工作频道，性质不同，所以仅查有没有敏感词不够。

PrivacyLens 的启发是从规则问答走到 agent actions：模型口头知道规范，执行任务时可能仍过度分享。

我会用相同内容改变 recipient、purpose 或授权，检查 agent 是否只发送完成任务必要的信息。这样既能测泄露，也能避免一个全删掉背景信息的系统虚假领先。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 为 synthetic users 生成同一信息在不同 recipients、purposes 与 explicit consents 下的 paired tasks。
- **Baselines / Ablations：** 比较 privacy prompt、PII redaction、contextual policy checker 和 minimal-disclosure action policy。
- **Metrics 与判读：** 测 unauthorized disclosure、necessary-information retention、正确拒绝和 task success。

## 追问与容易误判的地方

Privacy norms 依场景而变；本卡不是法律判断。实验标签需要明确来源、标注一致性和争议处理。

## 论文依据与适用范围

- [PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action](https://arxiv.org/abs/2409.00138) · 2024 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
