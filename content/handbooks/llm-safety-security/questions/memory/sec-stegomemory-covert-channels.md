---
id: sec-stegomemory-covert-channels
section: memory
order: 23
level: A
title: "StegoMemory：没有明显 secret 字符串，为什么仍需测 covert channels？"
quick: "这条近期 preprint 把问题从“有没有把 secret 原样写进去”推进到“memory 是否成了一个跨 session 的信息通道”。普通关键词扫描看不到，不代表接收方恢复不了。"
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
  - title: "StegoMemory: Agentic Memory Acts as Covert Steganographic Channel"
    url: "https://arxiv.org/abs/2610.04589"
    type: primary
---

## 题目描述

一个 memory note 看起来像正常摘要，但未来 agent 能从字词选择恢复其中的 synthetic hidden payload。

需要讨论：解释 covert transmission 的评价单位，设计不依赖敏感关键词匹配的实验。

## 回答思路

> **Situation：** 一个 memory note 看起来像正常摘要，但未来 agent 能从字词选择恢复其中的 synthetic hidden payload。  
> **Task：** 解释 covert transmission 的评价单位，设计不依赖敏感关键词匹配的实验。  
> **Approach / Why：** 在隔离环境中给 sender/receiver 分配独立上下文，使用随机 synthetic payload 和端到端恢复 oracle。  
> **Result / Check：** 分别测写入存活、retrieval、payload recovery 与正常任务完成，复现前不外推现实风险。

## 可以这样回答

这条近期 preprint 把问题从“有没有把 secret 原样写进去”推进到“memory 是否成了一个跨 session 的信息通道”。普通关键词扫描看不到，不代表接收方恢复不了。

我会让每个 episode 使用新的随机 synthetic payload，sender 和 receiver 的上下文严格隔离，确保接收方只能从 memory 得到信息。然后分别检查写入、持久化、检索和恢复。

最重要的对照是排除答案通过日志或共享 prompt 意外泄漏。没有做到隔离，所谓 covert-channel success 可能只是 evaluation bug。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 建立 sender→memory writer→store→receiver 四段隔离的 mock workflow，payload 每次随机生成。
- **Baselines / Ablations：** 加入 no-memory、randomized-memory、normalized summaries 和不知 payload 的 receiver。
- **Metrics 与判读：** 报告 exact/partial recovery、false recovery、memory survival 与 benign utility；对最新结果做独立复现。

## 追问与容易误判的地方

这是 2026-10 preprint，适合当 open research discussion；标题中的问题不能被当作所有 memory systems 已被攻破的证据。

## 论文依据与适用范围

- [StegoMemory: Agentic Memory Acts as Covert Steganographic Channel](https://arxiv.org/abs/2610.04589) · 2026 · preprint · 2026-10。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
