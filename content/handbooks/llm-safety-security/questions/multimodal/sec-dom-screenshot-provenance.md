---
id: sec-dom-screenshot-provenance
section: multimodal
order: 26
level: A
title: "DOM、screenshot、OCR 发生冲突时，agent 应信谁？"
quick: "我不会简单说 screenshot 一定更可信，或 DOM 一定更准确。页面本身就可能控制两者；冲突也可能来自 rendering、OCR 或 accessibility bug。"
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
  - title: "WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks"
    url: "https://arxiv.org/abs/2504.18575"
    type: primary
  - title: "Design Patterns for Securing LLM Agents against Prompt Injections"
    url: "https://arxiv.org/abs/2506.08837"
    type: primary
---

## 题目描述

页面可见按钮写着“保存草稿”，DOM label 却像“发布”；OCR、accessibility tree 与 tool response 的描述也不一致。

需要讨论：设计多种 observations 的 provenance 和 conflict resolution，说明如何评估安全与可用性。

## 回答思路

> **Situation：** 页面可见按钮写着“保存草稿”，DOM label 却像“发布”；OCR、accessibility tree 与 tool response 的描述也不一致。  
> **Task：** 设计多种 observations 的 provenance 和 conflict resolution，说明如何评估安全与可用性。  
> **Approach / Why：** 不要按 modality 固定信任级别；绑定动作到可验证目标和执行后的状态。  
> **Result / Check：** 记录 conflicting sources 与 resolution，检查真实副作用和可恢复性。

## 可以这样回答

我不会简单说 screenshot 一定更可信，或 DOM 一定更准确。页面本身就可能控制两者；冲突也可能来自 rendering、OCR 或 accessibility bug。

系统需要知道每份 observation 怎么生成、对应哪个页面状态。对高影响动作，可以用结构化 tool state 或执行前 preview 复核目标；仍有歧义时才请求更明确的信息。

研究中我会把恶意矛盾和正常 UI bug 放在一起测，避免 defense 只靠看到“不一致”就退出全部任务。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 在本地网页中分别制造 DOM label、可见文字、OCR 与 accessibility metadata 的受控冲突。
- **Baselines / Ablations：** 比较单一 modality、简单 majority vote、provenance-aware resolver 和执行前 state checks。
- **Metrics 与判读：** 测 wrong-target actions、safe completion、无害 UI inconsistency 下的误停和额外 observations 成本。

## 追问与容易误判的地方

多数来源可能都来自同一攻击者控制的页面，不能把它们当成独立证据进行“多数投票”。

## 论文依据与适用范围

- [WASP: Benchmarking Web Agent Security Against Prompt Injection Attacks](https://arxiv.org/abs/2504.18575) · 2025 · research paper。
- [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
