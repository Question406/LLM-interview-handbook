---
id: sec-skill-inject-supply-chain
section: tools
order: 16
level: S
title: "Skill-Inject：Skill 文件为什么既像文档，又像 supply-chain dependency？"
quick: "Skill 不只是给模型看的说明书，它还可能携带脚本、依赖和 tool bindings。文字会影响 planning，代码会直接产生 side effects，所以只扫描代码或只检测 prompt injection 都覆盖不完整。"
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
  - title: "Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks"
    url: "https://arxiv.org/abs/2602.20156"
    type: primary
---

## 题目描述

用户安装一个用于生成报告的 skill，包内同时包含说明、示例、脚本和外部依赖。

需要讨论：定义攻击者能改变的 artifacts，设计能区别合法 skill compliance 与恶意 instruction following 的 evaluation。

## 回答思路

> **Situation：** 用户安装一个用于生成报告的 skill，包内同时包含说明、示例、脚本和外部依赖。  
> **Task：** 定义攻击者能改变的 artifacts，设计能区别合法 skill compliance 与恶意 instruction following 的 evaluation。  
> **Approach / Why：** 将 skill 的 context influence 和代码执行分别建模，版本固定后做 matched benign/malicious tests。  
> **Result / Check：** 保留 legitimate task completion，并检查实际文件、网络和工具 side effects。

## 可以这样回答

Skill 不只是给模型看的说明书，它还可能携带脚本、依赖和 tool bindings。文字会影响 planning，代码会直接产生 side effects，所以只扫描代码或只检测 prompt injection 都覆盖不完整。

我会从一个能正常完成报告任务的 skill 出发，再在允许的 artifact 范围内加入可控变化。这样能区分 agent 是没理解 skill，还是确实拒绝了不属于任务的额外要求。

依赖和 skill 版本要固定，否则同一份题面可能实际执行不同内容，实验难以复现。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构建 benign skill 与仅一处改变的 variants，固定代码 hash、依赖和 mock filesystem/network。
- **Baselines / Ablations：** 比较 static text scan、code scan、runtime permissions 和联合策略。
- **Metrics 与判读：** 报告 legitimate compliance、unauthorized side effects、安装/加载/执行各阶段的触发率。

## 追问与容易误判的地方

“用户安装过”不等于对该 skill 的任何未来行为授权；但用户明确授权的必要动作也不应被当成攻击。

## 论文依据与适用范围

- [Skill-Inject: Measuring Agent Vulnerability to Skill File Attacks](https://arxiv.org/abs/2602.20156) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
