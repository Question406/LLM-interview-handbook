---
id: sec-cot-monitorability-faithfulness
section: alignment
order: 44
level: S
title: "CoT monitorability 与 faithfulness 是什么关系？"
quick: "我会把两个问题分开。Faithfulness 问文字是否准确反映产生答案的原因；monitorability 问这些文字是否足够帮助发现风险。前者不完美，不代表后者完全没用，但也不能靠读到一句安全解释就放心。"
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
  - title: "Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety"
    url: "https://arxiv.org/abs/2507.11473"
    type: primary
  - title: "MonitorBench: A Comprehensive Benchmark for Chain-of-Thought Monitorability in Large Language Models"
    url: "https://arxiv.org/abs/2603.28590"
    type: primary
---

## 题目描述

研究者想通过 agent 的 reasoning text 提前识别不安全行为，但模型不一定把所有决策过程写出来。

需要讨论：区分解释是否忠实、风险是否能被检测，以及 monitor 如何与 action/state observations 组合。

## 回答思路

> **Situation：** 研究者想通过 agent 的 reasoning text 提前识别不安全行为，但模型不一定把所有决策过程写出来。  
> **Task：** 区分解释是否忠实、风险是否能被检测，以及 monitor 如何与 action/state observations 组合。  
> **Approach / Why：** 将 CoT 当成可能有价值但不完整的观测信号，用多个 input views 做 ablation。  
> **Result / Check：** 在 fixed false-positive budget 下测 detection，并关注无 reasoning、压缩和 adaptive evasion。

## 可以这样回答

我会把两个问题分开。Faithfulness 问文字是否准确反映产生答案的原因；monitorability 问这些文字是否足够帮助发现风险。前者不完美，不代表后者完全没用，但也不能靠读到一句安全解释就放心。

实验可以让 monitor 分别看 action only、CoT only、CoT 加 action、完整 environment state，测每种信息带来的增益。

我尤其关心哪些设置下这个信号消失：reasoning 被压缩、任务很长、模型知道自己被监控，或者风险通过没有写出来的影响产生。执行端约束仍然需要保留。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 使用有确定 side-goal outcome 的 sandbox tasks，收集不同 reasoning budgets 与 formats 的 traces。
- **Baselines / Ablations：** 比较各信息视图、长度匹配对照、隐藏 outcome 的 judge，以及 adaptive red-team policies。
- **Metrics 与判读：** 报告 TPR at fixed FPR、提前量、utility、monitor cost 和 CoT 缺失时的 fallback。

## 追问与容易误判的地方

不要求披露任何私有模型的隐藏 reasoning；研究可使用公开可用或合成的 traces，并明确其代表性。

## 论文依据与适用范围

- [Chain of Thought Monitorability: A New and Fragile Opportunity for AI Safety](https://arxiv.org/abs/2507.11473) · 2025 · research paper。
- [MonitorBench: A Comprehensive Benchmark for Chain-of-Thought Monitorability in Large Language Models](https://arxiv.org/abs/2603.28590) · 2026 · COLM 2026。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
