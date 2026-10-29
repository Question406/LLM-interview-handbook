---
id: sec-computer-use-benign-context-risk
section: multimodal
order: 25
level: S
title: "OS-BLIND 与 OSGuard：正常 user request 为什么仍会导致 unsafe completion？"
quick: "这类 benchmark 的价值，是用户没有请求危险事情，风险来自当前环境和执行方式。比如删除同名临时文件在一个目录里合理，在共享目录里可能造成别人数据丢失。"
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
  - title: "The Blind Spot of Agent Safety: How Benign User Instructions Expose Critical Vulnerabilities in Computer-Use Agents"
    url: "https://arxiv.org/abs/2604.10577"
    type: primary
  - title: "OSGuard: A Benchmark for Safety in Computer-Use Agents"
    url: "https://arxiv.org/abs/2606.15034"
    type: primary
---

## 题目描述

用户只要求整理文件或更新表格，agent 却选了一个会破坏保护设置、误改共享资源的快捷操作。

需要讨论：解释 benign intent 与 state-dependent constraints 的关系，设计 action-level 与 trajectory-level 联合评估。

## 回答思路

> **Situation：** 用户只要求整理文件或更新表格，agent 却选了一个会破坏保护设置、误改共享资源的快捷操作。  
> **Task：** 解释 benign intent 与 state-dependent constraints 的关系，设计 action-level 与 trajectory-level 联合评估。  
> **Approach / Why：** 保持原始任务不变，在环境中加入可验证的风险状态，并确保安全路径存在。  
> **Result / Check：** 分别测单步判断与真实执行；同一个 action 在不同 state 下应有不同标签。

## 可以这样回答

这类 benchmark 的价值，是用户没有请求危险事情，风险来自当前环境和执行方式。比如删除同名临时文件在一个目录里合理，在共享目录里可能造成别人数据丢失。

我会同时评估“给定截图能否识别危险 action”与“运行整个任务能否始终保持约束”。前者好并不保证后者好，因为 agent 可能走进 evaluator 没见过的新状态。

最终安全判断应尽量基于环境状态和实际 side effects，而不是看 agent 有没有说“我会小心操作”。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 为正常 computer-use tasks 添加只改变安全条件的 environment variants，保留安全完成路线。
- **Baselines / Ablations：** 比较 no guardrail、单步 visual monitor、带历史的 monitor 和结构化 resource policy。
- **Metrics 与判读：** 报告 safe completion、unsafe completion、错误拦截、state-shift 下单步误差和 end-to-end 开销。

## 追问与容易误判的地方

OS-BLIND 与 OSGuard 的任务和评分不同；分别解释各自测什么，再讨论互补性，不直接横比 headline ASR。

## 论文依据与适用范围

- [The Blind Spot of Agent Safety: How Benign User Instructions Expose Critical Vulnerabilities in Computer-Use Agents](https://arxiv.org/abs/2604.10577) · 2026 · preprint。
- [OSGuard: A Benchmark for Safety in Computer-Use Agents](https://arxiv.org/abs/2606.15034) · 2026 · preprint · revision 2026-10。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
