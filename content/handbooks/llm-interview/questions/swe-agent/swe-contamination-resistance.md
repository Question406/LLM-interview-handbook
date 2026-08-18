---
id: swe-contamination-resistance
section: swe-agent
order: 3
level: A
title: 为什么静态 SWE 集很容易发生训练污染，如何构建并报告一个 contamination-resistant 的持续 benchmark？
quick: GitHub issue、PR 和测试通常公开，模型可能记住答案。采用时间截断、近期/未见仓库、冻结提交与隐藏测试，明确训练 cutoff；把 frozen leaderboard 与持续 live eval 分开报告。
tags:
  - SWE Agent
  - Contamination
  - Benchmark
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: SWE-bench Multimodal
    url: https://arxiv.org/abs/2505.23419
    type: primary
---

代码任务天然高风险：issue、最终 PR、讨论和测试都可能在预训练/后训练语料中出现。模型生成相似 patch 不一定代表在线诊断与修复能力。

建立 benchmark 时锁定任务的发布日期，声明模型训练知识截止；优先使用新近 issue、未见仓库或私有/hidden evaluation，并冻结 repo/test commit。对公开集合做字符串、AST、embedding 和 patch 检索审计只能提供证据，不能证明绝对无污染。

报告需要区分离线冻结分数、时间后续 live 分数和污染审计结果。不要把后者较低解释为模型退化，它通常更接近真实泛化难度。
