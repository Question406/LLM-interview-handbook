---
id: sec-privileged-quarantined-models
section: defenses
order: 29
level: S
title: "Dual LLM：让一个 model 只读不可信数据就够了吗？"
quick: "隔离 worker 的好处很直接：它即使被网页影响，也没有外发或写入权限。但如果 controller 把 worker 返回的任意 string 当成新命令，风险只是换了一次传输。"
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
  - title: "Defeating Prompt Injections by Design (CaMeL)"
    url: "https://arxiv.org/abs/2503.18813"
    type: primary
  - title: "Design Patterns for Securing LLM Agents against Prompt Injections"
    url: "https://arxiv.org/abs/2506.08837"
    type: primary
---

## 题目描述

系统让 worker model 读取网页，只把结构化摘要传给能调用 tools 的 controller model。

需要讨论：解释这个隔离减少了什么风险、哪些信息仍可能通过摘要影响 controller。

## 回答思路

> **Situation：** 系统让 worker model 读取网页，只把结构化摘要传给能调用 tools 的 controller model。  
> **Task：** 解释这个隔离减少了什么风险、哪些信息仍可能通过摘要影响 controller。  
> **Approach / Why：** 限制 worker 的 capability，同时约束传回的数据结构、解释方式与后续允许动作。  
> **Result / Check：** 用合法 schema 内的 malicious values 测试，不只尝试塞入明显命令。

## 可以这样回答

隔离 worker 的好处很直接：它即使被网页影响，也没有外发或写入权限。但如果 controller 把 worker 返回的任意 string 当成新命令，风险只是换了一次传输。

我会规定 worker 返回哪些 typed fields、这些 fields 可以影响什么，并在执行端继续检查 resource 和 destination。比如“推荐收件人”本身就可能改变授权对象，不能因为放在 JSON 里就算安全。

所以 dual LLM 是有用的架构组件，完整性来自数据流规则和 capability 限制，而不是模型数量变成两个。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** Worker 无 side-effect tools，输出固定 schema；加入内容 benign、schema-valid malicious values 和 malformed outputs。
- **Baselines / Ablations：** 比较单模型、双模型任意摘要、typed outputs、typed outputs + executor checks。
- **Metrics 与判读：** 报告 unauthorized parameter influence、safe completion、额外 token/latency 与 worker hallucination。

## 追问与容易误判的地方

Schema 可以缩小输入语言，但对具有指令语义的自由文本字段仍需处理；结构化不等于授权。

## 论文依据与适用范围

- [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813) · 2025 · research paper。
- [Design Patterns for Securing LLM Agents against Prompt Injections](https://arxiv.org/abs/2506.08837) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
