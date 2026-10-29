---
id: sec-mcp-tool-metadata-poisoning
section: tools
order: 13
level: S
title: "MCPTox：为什么没有调用的 tool 也能影响 agent？"
quick: "Agent 往往在选择工具之前就读取 description，所以恶意影响可以发生在 discovery 阶段。攻击者不必让自己的工具被调用，只要文字改变了 agent 怎样使用已有工具，就可能达成目标。"
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
  - title: "MCPTox: A Benchmark for Tool Poisoning Attack on Real-World MCP Servers"
    url: "https://arxiv.org/abs/2508.14925"
    type: primary
---

## 题目描述

Agent 发现一批 MCP tools。某个工具只是在 description 里提供了看似必要的操作说明，却改变了 agent 对其他工具的调用。

需要讨论：解释 discovery-time exposure、tool selection 与 tool-output injection 的区别，提出测量方式。

## 回答思路

> **Situation：** Agent 发现一批 MCP tools。某个工具只是在 description 里提供了看似必要的操作说明，却改变了 agent 对其他工具的调用。  
> **Task：** 解释 discovery-time exposure、tool selection 与 tool-output injection 的区别，提出测量方式。  
> **Approach / Why：** 把 tool metadata 当作独立 untrusted input，分别控制可见性和执行权限。  
> **Result / Check：** 比较未执行但可见、完全不可见和执行后可见三种设置。

## 可以这样回答

Agent 往往在选择工具之前就读取 description，所以恶意影响可以发生在 discovery 阶段。攻击者不必让自己的工具被调用，只要文字改变了 agent 怎样使用已有工具，就可能达成目标。

我会把 metadata 的来源、版本和实际进入 context 的内容都记录下来，再看它是否影响 tool choice 或 arguments。单纯禁止执行这个工具，未必消除已经读过 description 的影响。

防御需要同时考虑 discovery 和 execution：description 帮助理解用途，真正可执行权限仍由 trusted registry 和 action policy 决定。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 在相同可用工具集合中替换一个 description，使用 mock tools 和 synthetic resources。
- **Baselines / Ablations：** 比较 poisoned tool visible-but-disabled、hidden、enabled，以及 metadata scanner / schema isolation。
- **Metrics 与判读：** 报告 exposure、selection changes、其他工具的违规调用、safe completion 与发现阶段开销。

## 追问与容易误判的地方

认证了 server 身份，只能说明 metadata 来自谁；不能证明描述里的指令符合当前用户授权。

## 论文依据与适用范围

- [MCPTox: A Benchmark for Tool Poisoning Attack on Real-World MCP Servers](https://arxiv.org/abs/2508.14925) · 2025 · research paper。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
