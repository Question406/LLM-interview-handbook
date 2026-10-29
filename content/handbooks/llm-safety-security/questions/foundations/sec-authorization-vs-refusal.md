---
id: sec-authorization-vs-refusal
section: foundations
order: 3
level: S
title: "Agent 会拒绝危险问题，为什么仍可能执行 unauthorized actions？"
quick: "我会把“知道不能做”与“这次操作是否被授权”分开。Refusal training 可以让模型识别明显有害的请求，但发送摘要本身很正常，问题可能藏在 recipient、附件或多带的一条个人信息里。"
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
  - title: "The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions"
    url: "https://arxiv.org/abs/2404.13208"
    type: primary
  - title: "PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action"
    url: "https://arxiv.org/abs/2409.00138"
    type: primary
---

## 题目描述

Agent 能正确回答“不能随意分享私人信息”，却在完成会议摘要时把不必要的个人信息发给了外部联系人。

需要讨论：解释 refusal alignment、task authorization 与 contextual privacy 的区别，提出执行时的检查位置。

## 回答思路

> **Situation：** Agent 能正确回答“不能随意分享私人信息”，却在完成会议摘要时把不必要的个人信息发给了外部联系人。  
> **Task：** 解释 refusal alignment、task authorization 与 contextual privacy 的区别，提出执行时的检查位置。  
> **Approach / Why：** 将模型的语义判断与 executor 的 resource/action/recipient policy 分开。  
> **Result / Check：** 看实际 side effect 与收件人获得的数据，不能只看最终回复中的拒绝语句。

## 可以这样回答

我会把“知道不能做”与“这次操作是否被授权”分开。Refusal training 可以让模型识别明显有害的请求，但发送摘要本身很正常，问题可能藏在 recipient、附件或多带的一条个人信息里。

执行端需要检查是谁授权、针对哪个资源、能做什么、数据可以发给谁。模型生成的自然语言理由可以帮助审查，不能自己扩大可执行权限。

测试时我会检查实际发送记录和接收方可见的数据。Agent 一边说会保护隐私、一边已经调用工具发出内容，这仍然是失败。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构造同一摘要在内部同事、外部客户和公共频道三个 recipients 下的合法/非法 variants。
- **Baselines / Ablations：** 比较 refusal-only、prompt policy、tool policy enforcement 和两者结合。
- **Metrics 与判读：** 用实际 tool arguments 与可见性状态判定违规，补充 over-refusal、任务完成和必要信息保留率。

## 追问与容易误判的地方

用户确实可以授权某些敏感分享。Policy 应表达具体授权与目的，不应把所有敏感字段一律删除。

## 论文依据与适用范围

- [The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions](https://arxiv.org/abs/2404.13208) · 2024 · research paper。
- [PrivacyLens: Evaluating Privacy Norm Awareness of Language Models in Action](https://arxiv.org/abs/2409.00138) · 2024 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
