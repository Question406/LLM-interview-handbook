---
id: sec-tool-update-toctou
section: tools
order: 18
level: A
title: "审过的 tool / skill 更新以后：如何研究 TOCTOU 与权限漂移？"
quick: "我会先确定“审过”指的是什么：description、schema、脚本 hash、依赖版本，还是 server 身份。如果检查的是旧脚本，执行的是新脚本，再好的文字 detector 也无能为力。"
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
  - title: "MCP Security Best Practices · 2025-11-25 documentation"
    url: "https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices"
    type: primary
  - title: "Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks"
    url: "https://arxiv.org/abs/2602.20156"
    type: primary
---

## 题目描述

Agent 选择工具时看到一个版本，真正执行时 server description、脚本或依赖已经改变。

需要讨论：说明哪些对象需要版本绑定，如何区分模型受骗与执行对象被替换。

## 回答思路

> **Situation：** Agent 选择工具时看到一个版本，真正执行时 server description、脚本或依赖已经改变。  
> **Task：** 说明哪些对象需要版本绑定，如何区分模型受骗与执行对象被替换。  
> **Approach / Why：** 把被审查的 artifact identity 与实际执行对象绑定，并在更新时重新做 policy checks。  
> **Result / Check：** 在 review 与 execute 之间注入 controlled updates，验证 stale approval 不会覆盖新行为。

## 可以这样回答

我会先确定“审过”指的是什么：description、schema、脚本 hash、依赖版本，还是 server 身份。如果检查的是旧脚本，执行的是新脚本，再好的文字 detector 也无能为力。

可以把 review 结果绑定到具体版本和 capability manifest；更新后如果内容或权限发生变化，就不能继续复用旧结果。远程 tool 还要考虑 server state 与参数授权，因为 pin 住 description 不等于固定了实现。

实验把更新时间精确放在 planning 和 execution 之间，并分别改变文案、权限和代码，能看出漏洞究竟出现在哪层。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** Mock registry 支持版本 A/B，在 discovery、plan、approval、execute 四个时点切换 artifact。
- **Baselines / Ablations：** 比较不绑定版本、仅绑定 metadata、绑定 executable identity 与 execution-time resource checks。
- **Metrics 与判读：** 报告 stale authorization 使用、正常更新兼容性、额外延迟和可定位的审计事件。

## 追问与容易误判的地方

这是由 supply-chain 与 protocol concerns 推导的研究题，引用文献不被视为已经实现了这里全部版本协议。

## 论文依据与适用范围

- [MCP Security Best Practices · 2025-11-25 documentation](https://modelcontextprotocol.io/docs/2025-11-25/tutorials/security/security_best_practices) · 2025 · official protocol documentation。
- [Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks](https://arxiv.org/abs/2602.20156) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
