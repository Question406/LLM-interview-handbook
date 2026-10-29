---
id: sec-proposal-multimodal-agent-safety
section: projects
order: 55
level: S
title: "Research proposal：给 browser / computer-use agent 做 state-aware safety dataset"
quick: "我会从“这个画面里的动作是否对当前任务安全”切入。一个样本需要的不只是 screenshot，还包括用户目标、candidate action、目标资源、当前可见性和执行后的状态变化。"
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
  - title: "WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks"
    url: "https://arxiv.org/abs/2504.18575"
    type: primary
  - title: "OSGuard: A Benchmark for Safety in Computer-Use Agents"
    url: "https://arxiv.org/abs/2606.15034"
    type: primary
---

## 题目描述

你想做一个与 multimodal tool use 有关的数据项目，避免停留在给图片加一句恶意文字。

需要讨论：设计 observation、action、state constraints 与 replayable environment 的数据 schema。

## 回答思路

> **Situation：** 你想做一个与 multimodal tool use 有关的数据项目，避免停留在给图片加一句恶意文字。  
> **Task：** 设计 observation、action、state constraints 与 replayable environment 的数据 schema。  
> **Approach / Why：** 让同一个可见 action 在不同权限和环境 state 下有不同标签，同时保持正常任务可完成。  
> **Result / Check：** 测试 unseen applications、rendering changes 与 end-to-end safe completion，而不只分类截图。

## 可以这样回答

我会从“这个画面里的动作是否对当前任务安全”切入。一个样本需要的不只是 screenshot，还包括用户目标、candidate action、目标资源、当前可见性和执行后的状态变化。

可以在本地网页环境里做少量真实可重放 workflows：正常任务不变，改共享权限、目标对象或发布状态。再收集 screenshot、DOM 和结构化 state，研究哪些 observations 真正帮助判断。

这个 setting 同时连接视觉理解、工具参数 grounding 和 authorization。第一版只承诺做出可靠数据与 baseline，不提前承诺防住所有 visual attacks。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 建立 10 个本地 workflows，每个合法/风险 state、两种 rendering 和 clean/injected observation variants。
- **Baselines / Ablations：** 比较 screenshot-only、DOM-only、融合模型、state-aware checker 和无 guardrail agent。
- **Metrics 与判读：** 测 action-level accuracy、错误对象定位、state-shift generalization、safe completion 与运行成本。

## 追问与容易误判的地方

给 monitor 的 privileged state 如果部署时拿不到，应作为 oracle upper baseline 单独标注。

## 论文依据与适用范围

- [WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks](https://arxiv.org/abs/2504.18575) · 2025 · research paper。
- [OSGuard: A Benchmark for Safety in Computer-Use Agents](https://arxiv.org/abs/2606.15034) · 2026 · preprint · revision 2026-10。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
