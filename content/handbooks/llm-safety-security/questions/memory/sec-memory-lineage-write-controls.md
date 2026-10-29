---
id: sec-memory-lineage-write-controls
section: memory
order: 21
level: S
title: "Memory defenses 应放在 write、retrieval，还是 action time？"
quick: "我会先把 memory 分成内容和受控 metadata。内容可以 summarise，来源、所属用户、允许用途和有效期不能仅靠模型在正文里自述，否则一次总结就可能把外部说法变成“系统记得”。"
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
  - title: "Poison Once, Exploit Forever: Environment-Injected Memory Poisoning Attacks on Web Agents"
    url: "https://arxiv.org/abs/2604.02623"
    type: primary
  - title: "Defeating Prompt Injections by Design (CaMeL)"
    url: "https://arxiv.org/abs/2503.18813"
    type: primary
---

## 题目描述

一个可疑 observation 被 summarizer 写成普通事实，原始网页链接和 trust 信息在 compaction 后消失了。

需要讨论：设计保留 lineage 的 memory schema，比较 write-time filtering、retrieval-time checks 与 action enforcement。

## 回答思路

> **Situation：** 一个可疑 observation 被 summarizer 写成普通事实，原始网页链接和 trust 信息在 compaction 后消失了。  
> **Task：** 设计保留 lineage 的 memory schema，比较 write-time filtering、retrieval-time checks 与 action enforcement。  
> **Approach / Why：** 将来源与权限属性作为受控 metadata 持续传播，读取后仍执行独立 action policy。  
> **Result / Check：** 测 provenance survival、跨 session 违规和正常 memory utility，检查未标记数据的默认处理。

## 可以这样回答

我会先把 memory 分成内容和受控 metadata。内容可以 summarise，来源、所属用户、允许用途和有效期不能仅靠模型在正文里自述，否则一次总结就可能把外部说法变成“系统记得”。

Write-time filter 能减少进入记忆的坏记录，retrieval-time check 能考虑当前任务，但它们都不该自动授予执行权限。最后的 action 仍要检查 resource 和 destination。

对 lineage 的测试也要包含 compaction 和多次改写：第一次写入很干净，不代表第五次总结后还知道原始来源。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 将 synthetic observations 写入 memory，重复 summarization 与跨 session retrieval，保留可对照的原始事件。
- **Baselines / Ablations：** 分别启用 write filter、typed lineage、retrieval check、action policy，以及组合。
- **Metrics 与判读：** 报告 lineage retention、false trust promotion、cross-session ASR 和完成依赖记忆的正常任务比例。

## 追问与容易误判的地方

签名能证明记录来自哪个组件，不能保证记录真实、适用于当前任务，或写入过程没有受到 injection。

## 论文依据与适用范围

- [Poison Once, Exploit Forever: Environment-Injected Memory Poisoning Attacks on Web Agents](https://arxiv.org/abs/2604.02623) · 2026 · preprint。
- [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
