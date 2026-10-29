---
id: sec-judge-robustness-state-oracles
section: evaluation
order: 39
level: S
title: "LLM-as-judge 自己也会被 injection：security evaluator 应怎么写？"
quick: "我会尽量让实际事件说话：有没有发出、发给谁、有没有删除、状态是否改变，这些通常比语言 judge 更可靠。语义 judge 留给需要理解意图或部分泄露的 cases。"
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
  - title: "PIArena: A Platform for Prompt Injection Evaluation"
    url: "https://aclanthology.org/2026.acl-long.1533/"
    type: primary
  - title: "OSGuard: A Benchmark for Safety in Computer-Use Agents"
    url: "https://arxiv.org/abs/2606.15034"
    type: primary
---

## 题目描述

Evaluator 读取完整 attack transcript，里面也有让“评测员判为安全”的文本；最终回复与真实工具行为还可能不一致。

需要讨论：设计 deterministic state checks 与 semantic judge 的分工，以及 judge attack tests。

## 回答思路

> **Situation：** Evaluator 读取完整 attack transcript，里面也有让“评测员判为安全”的文本；最终回复与真实工具行为还可能不一致。  
> **Task：** 设计 deterministic state checks 与 semantic judge 的分工，以及 judge attack tests。  
> **Approach / Why：** 把可判定的副作用交给环境 oracle；语义判定器使用明确 schema、隔离输入与人工校准。  
> **Result / Check：** 用 adversarial transcripts 和已知 ground-truth cases 测 evaluator，而不只测 agent。

## 可以这样回答

我会尽量让实际事件说话：有没有发出、发给谁、有没有删除、状态是否改变，这些通常比语言 judge 更可靠。语义 judge 留给需要理解意图或部分泄露的 cases。

Judge 读的是不可信 transcript，所以也要测试它会不会跟随里面的评测指令。输入被放进 JSON 仍不代表语义上安全，需要隔离评分规则，并用受控 adversarial cases 验证。

最后公开 judge agreement、disagreements 和人工抽样结果。一个漂亮的 ASR 数字，如果 evaluator 会被 payload 改判，就没有解释力。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 创建明确 success/failure 的 mock traces，再加入针对 evaluator 的无副作用指令与引用干扰。
- **Baselines / Ablations：** 比较 final-answer judge、full-trace judge、deterministic state oracle 和联合评分。
- **Metrics 与判读：** 测 false safe、false unsafe、judge injection success、人工 agreement 和 scorer-version sensitivity。

## 追问与容易误判的地方

用另一个更强模型打分是有用 baseline，但不能只凭模型更强就假设其评分独立且可靠。

## 论文依据与适用范围

- [PIArena: A Platform for Prompt Injection Evaluation](https://aclanthology.org/2026.acl-long.1533/) · 2026 · ACL 2026。
- [OSGuard: A Benchmark for Safety in Computer-Use Agents](https://arxiv.org/abs/2606.15034) · 2026 · preprint · revision 2026-10。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
