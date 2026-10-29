---
id: sec-classifier-cascades-calibration
section: defenses
order: 33
level: S
title: "Constitutional Classifiers++：为什么用 exchange context 与 classifier cascade？"
quick: "只看当前一句话可能不知道它与前文组合后意味着什么。Exchange classifier 读到更完整的上下文，能判断这次回答究竟在帮助谁完成什么。"
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
  - title: "Constitutional Classifiers: Defending against Universal Jailbreaks across Thousands of Hours of Red Teaming"
    url: "https://arxiv.org/abs/2501.18837"
    type: primary
  - title: "Constitutional Classifiers++: Efficient Production-Grade Defenses against Universal Jailbreaks"
    url: "https://arxiv.org/abs/2601.04603"
    type: primary
---

## 题目描述

一个 guardrail 只看最新输出就漏掉跨多轮组合的风险；换成大模型看完整 context 后成本又很高。

需要讨论：解释 full-exchange judgement 与分级检测的收益，设计 threshold 和成本控制实验。

## 回答思路

> **Situation：** 一个 guardrail 只看最新输出就漏掉跨多轮组合的风险；换成大模型看完整 context 后成本又很高。  
> **Task：** 解释 full-exchange judgement 与分级检测的收益，设计 threshold 和成本控制实验。  
> **Approach / Why：** 用低成本 classifier 处理常见 cases，把不确定输入升级给更强判定器，按 held-out traffic 校准。  
> **Result / Check：** 同时测 miss rate、false refusal、escalation rate 和端到端成本。

## 可以这样回答

只看当前一句话可能不知道它与前文组合后意味着什么。Exchange classifier 读到更完整的上下文，能判断这次回答究竟在帮助谁完成什么。

Cascade 则把成本分配给更难的 cases：先用轻量判断，再升级给昂贵模型。关键是升级规则是否把新型攻击也送上去，而不是只对旧攻击模式敏感。

我会在真实分布的正常样本和 defense-aware attacks 上分别调 threshold、留出测试；不能用同一批 attacks 一边选阈值一边报告成功。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 准备多轮 exchanges、孤立看无害但组合危险的 cases，以及正常业务 traffic 样本。
- **Baselines / Ablations：** 比较 output-only、full-exchange、single heavy classifier、cascade 和 probe/external ensemble。
- **Metrics 与判读：** 在固定 false-positive 或 latency budget 下测 attack miss、escalation、p95 latency 与 token cost。

## 追问与容易误判的地方

原研究的“universal jailbreak 没找到”使用特定成功标准；不能换成单次成功率为零。

## 论文依据与适用范围

- [Constitutional Classifiers: Defending against Universal Jailbreaks across Thousands of Hours of Red Teaming](https://arxiv.org/abs/2501.18837) · 2025 · research paper。
- [Constitutional Classifiers++: Efficient Production-Grade Defenses against Universal Jailbreaks](https://arxiv.org/abs/2601.04603) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
