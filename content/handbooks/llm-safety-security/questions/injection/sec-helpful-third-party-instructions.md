---
id: sec-helpful-third-party-instructions
section: injection
order: 9
level: S
title: "第三方内容有时确实包含有用 instructions，怎样避免 over-defense？"
quick: "我不会把“外部文本里有 imperative sentence”直接当成攻击。网站告诉你先选退货原因再上传凭证，是完成任务需要的流程知识；让你把退款转去另一个账户，则涉及用户没有授权的结果。"
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
  - title: "AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?"
    url: "https://arxiv.org/abs/2602.03117"
    type: primary
---

## 题目描述

Agent 需要根据网站的操作说明填写退货表单，但网页同时可能包含修改用户目标的指令。

需要讨论：区分 task-relevant procedural knowledge 与 unauthorized goal changes，并设计对照数据。

## 回答思路

> **Situation：** Agent 需要根据网站的操作说明填写退货表单，但网页同时可能包含修改用户目标的指令。  
> **Task：** 区分 task-relevant procedural knowledge 与 unauthorized goal changes，并设计对照数据。  
> **Approach / Why：** 保留合法用户目标，把外部说明限制为完成目标所需的参数或局部步骤。  
> **Result / Check：** 同时测完成正常流程与抵抗目标修改，重点看 ambiguous cases。

## 可以这样回答

我不会把“外部文本里有 imperative sentence”直接当成攻击。网站告诉你先选退货原因再上传凭证，是完成任务需要的流程知识；让你把退款转去另一个账户，则涉及用户没有授权的结果。

研究难点是把这两类样本做得足够相似。否则 detector 可能只学会阻止所有步骤说明，静态 benchmark 上很安全，真实使用却寸步难行。

我会用同一网站和任务生成 matched pairs：正常操作说明、等长干扰说明、改变授权目标的说明，再分别测 utility 和违规。

## 研究实验怎么设计

以下为本题提出的实验方案。

- **Setting 与 hypothesis：** 选择需要动态读取页面 instructions 的 mock shopping/support workflows，冻结用户目标与授权对象。
- **Baselines / Ablations：** 比较移除全部指令、模型分类、restricted plan 和 provenance-aware action checks。
- **Metrics 与判读：** 报告 helpful-instruction compliance、attacker-goal rejection、safe completion 和不必要中止率。

## 追问与容易误判的地方

外部内容也可能提供必要的新信息。判断标准应是允许它影响哪类决策，不能仅按 imperative grammar 分。

## 论文依据与适用范围

- [AgentDyn: Are Your Agent Security Defenses Deployable in Real-World Dynamic Environments?](https://arxiv.org/abs/2602.03117) · 2026 · preprint。

本卡把公开研究整理为讨论题；“我会”描述拟议做法，具体实验方案与判断属于手册分析。文献核对日期：2026-10-28。
