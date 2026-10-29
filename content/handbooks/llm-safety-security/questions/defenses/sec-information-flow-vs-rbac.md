---
id: sec-information-flow-vs-rbac
section: defenses
order: 31
level: A
title: "RBAC、capabilities 与 information-flow control 分别解决什么？"
quick: "我会用这个例子说明只看单个 action permissions 为什么不够：read 合法、send 也合法，read 的内容流进 send 却可能非法。Information-flow policy 关心的是这种组合。"
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
  - title: "MCP Security Best Practices · 2025-11-25 documentation"
    url: "https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices"
    type: primary
---

## 题目描述

Agent 有权读取内部文件，也有权发送外部邮件，但没有权把该文件内容发给外部联系人。

需要讨论：说明 access control 与数据流限制的区别，以及组合后还剩哪些难点。

## 回答思路

> **Situation：** Agent 有权读取内部文件，也有权发送外部邮件，但没有权把该文件内容发给外部联系人。  
> **Task：** 说明 access control 与数据流限制的区别，以及组合后还剩哪些难点。  
> **Approach / Why：** 用 capabilities 限制资源动作，用 labels/policies 约束数据从 source 到 sink 的传播。  
> **Result / Check：** 检查 transformations、summaries 与 implicit control flows，不只检查原始字符串。

## 可以这样回答

我会用这个例子说明只看单个 action permissions 为什么不够：read 合法、send 也合法，read 的内容流进 send 却可能非法。Information-flow policy 关心的是这种组合。

Capabilities 可以把可访问资源和操作限制得很具体；数据 labels 则需要随读取、合并和总结传播。对外发出之前，检查接收方是否允许获得这些来源的数据。

难点在派生信息：摘要、统计甚至分支选择都可能带来信息。Reference 系统需要明确哪些 transformations 会保留标记、什么时候允许 declassification，以及尚未处理的侧信道。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 设计 read/internal、read/public、send/external 的合法单动作与非法组合，使用 synthetic labeled records。
- **Baselines / Ablations：** 比较 RBAC-only、resource capabilities、explicit-flow tracking 和更严格的 control-flow tracking。
- **Metrics 与判读：** 测 direct/derived leakage、合法聚合受阻率、declassification 需求和运行开销。

## 追问与容易误判的地方

“可以读”不等于“可以传播”；反过来，把任何依赖敏感输入的结果全部永久封锁，也可能让正常应用不可用。

## 论文依据与适用范围

- [Defeating Prompt Injections by Design (CaMeL)](https://arxiv.org/abs/2503.18813) · 2025 · research paper。
- [MCP Security Best Practices · 2025-11-25 documentation](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) · 2025 · official protocol documentation。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
