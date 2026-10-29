---
id: sec-role-confusion-probes
section: injection
order: 8
level: A
title: "Role Confusion：role tags 为什么可能不足，怎样验证机制解释？"
quick: "这条研究线很有意思的地方，是它把“文本标签写成 tool”与“模型内部把它当谁在说话”分开。Role Confusion 论文用 role probes 研究这种差异，而不是只把每个成功 payload 当成孤立案例。"
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
  - title: "Prompt Injection as Role Confusion"
    url: "https://arxiv.org/abs/2603.12277"
    type: primary
---

## 题目描述

同样一句第三方指令，换成像用户消息或模型 reasoning 的语气后，agent 更容易跟随它。

需要讨论：解释 role perception 的研究假设，并设计能区分 style correlation 与 causal mechanism 的实验。

## 回答思路

> **Situation：** 同样一句第三方指令，换成像用户消息或模型 reasoning 的语气后，agent 更容易跟随它。  
> **Task：** 解释 role perception 的研究假设，并设计能区分 style correlation 与 causal mechanism 的实验。  
> **Approach / Why：** 固定语义与角色标签改变写作风格，结合 probes 和受控 interventions。  
> **Result / Check：** 在未见 templates、模型和 benign role text 上验证预测与干预效果。

## 可以这样回答

这条研究线很有意思的地方，是它把“文本标签写成 tool”与“模型内部把它当谁在说话”分开。Role Confusion 论文用 role probes 研究这种差异，而不是只把每个成功 payload 当成孤立案例。

我会固定恶意目标、长度和 role tags，改写同一内容的风格，看成功率和 probe signal 是否一起变化。然后再做能改变表示、但尽量不破坏语言能力的 intervention。

如果 probe 只在已经见过的模板上预测成功，或者 intervention 同时让模型不会调用工具，就还不足以支持机制解释。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 构建语义匹配的 user-like、tool-like、reasoning-like 和普通引用文本，保留真实 message roles。
- **Baselines / Ablations：** 加入 shuffled-label probes、等维随机 directions、无 probe baseline，以及跨模型测试。
- **Metrics 与判读：** 比较 held-out prediction、intervention 后 ASR、utility 和 role-recognition accuracy；相关性与因果证据分别报告。

## 追问与容易误判的地方

Probe 能读出信息，不代表 agent 决策一定使用了这条信息；还要排除长度、困惑度和模板特征的混杂。

## 论文依据与适用范围

- [Prompt Injection as Role Confusion](https://arxiv.org/abs/2603.12277) · 2026 · ICML 2026。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
