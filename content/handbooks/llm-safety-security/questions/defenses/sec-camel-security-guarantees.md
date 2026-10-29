---
id: sec-camel-security-guarantees
section: defenses
order: 28
level: S
title: "CaMeL 的关键思想是什么，所谓 provable security 究竟依赖什么？"
quick: "我会把 CaMeL 的核心讲成：不要让读到的外部文字直接决定接下来拥有什么权力、可以执行什么动作。它把 control/data flows 显式化，再用 capabilities 限制数据能流向哪里。"
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
---

## 题目描述

一个 assistant 需要读不可信邮件、提取信息，再对文件或外部服务执行操作。

需要讨论：解释 control/data separation、capabilities 与 trusted computing base，指出 guarantee 的适用范围。

## 回答思路

> **Situation：** 一个 assistant 需要读不可信邮件、提取信息，再对文件或外部服务执行操作。  
> **Task：** 解释 control/data separation、capabilities 与 trusted computing base，指出 guarantee 的适用范围。  
> **Approach / Why：** 从 trusted request 构造受控程序，对外部数据做标记并在数据流与动作处执行 policies。  
> **Result / Check：** 分开验证模型规划、interpreter 和 policy correctness；检查 exceptions 与 side channels。

## 可以这样回答

我会把 CaMeL 的核心讲成：不要让读到的外部文字直接决定接下来拥有什么权力、可以执行什么动作。它把 control/data flows 显式化，再用 capabilities 限制数据能流向哪里。

安全保证不是“LLM 以后不会受骗”，而是在规定的攻击模型下，执行层仍能阻止违反 policy 的数据流。Policy 本身、interpreter 实现和 tools 的真实语义都属于需要信任或验证的部分。

所以读论文时我会同时看 threat model、non-goals 和 side channels。部署一个近似版本，再引用原论文的保证，并不成立。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 选取 read→extract→write/send 的 sandbox workflows，列明 trusted inputs、labels、sinks 与允许的数据流。
- **Baselines / Ablations：** 比较 prompt-only、dual-model、带 policy 的信息流控制；分别移除关键 checks。
- **Metrics 与判读：** 报告 policy violations、safe completion、额外 calls/latency 与不在保证内的失败类型。

## 追问与容易误判的地方

论文的研究代码也有实现局限。形式模型的性质、artifact 的正确性与产品可部署性，是三件需要分别提供证据的事。

## 论文依据与适用范围

- [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
