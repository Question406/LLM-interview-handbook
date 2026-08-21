---
id: ali-score-vs-agent
section: alibaba
order: 24
level: A
title: 单次 LLM 打分算不算 Agent？和多轮工具 Agent 的核心区别？
quick: 单次打分更像一次性推理/判别；Agent 强调多步决策、与环境交互、状态更新与终止条件。差别在控制回路，不在是否调用了一次模型。
tags:
  - Alibaba
  - Agent
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---

陷阱是把「用了 LLM」或「调了一次 function calling」等同于 Agent。单次 LLM 打分更像一次性推理 / 判别；Agent 强调多步决策、与环境交互、状态更新与终止条件。差别在控制回路，不在是否调用了一次模型。面试先和面试官对齐定义，避免各说各的。规划与状态机见 `ali-modular-agent-plan`，Skill / Memory / RAG 也不等于 Agent 回路，见 `ali-skill-memory-rag`。

## 差别在控制回路

可用定义：单次打分无环境反馈闭环，或只有一次 forward；Agent 是 observe → act → observe 循环，工具 / 用户 / 环境改变 state，并且有终止条件。输入固定、输出一个分数或标签、没有后续动作时，叫判别器 / 打分器即可。一旦系统要根据观察选工具、改状态、决定何时停，才按 Agent 设计权限和停止条件。用 LLM 给商品评论打 1 到 5 分，不再查库存、不再问用户，这不是 Agent。同一个模型若先查订单、再决定是否调用退货工具、等用户确认后才提交，这才是 Agent——要讲清状态、动作空间、停止条件与责任边界。

## 一次工具也不自动等于 Agent

带一次检索的打分（先搜政策再打「是否可退」）有环境反馈，但若没有多步决策和终止策略，仍更接近工具增强判别。关键看有没有循环：是否根据新观察改变下一步，是否可能再问、再调、再停。把一次 FC 也叫做 Agent，后续安全评审会漏掉循环里的重复执行和权限升级——打分器通常只读，Agent 可能对同一订单调两次退款。权限与 HITL 应按「会不会形成回路」升级，见 `ali-guardrail`、`ali-hitl-risk`。

## 对齐定义再谈权限

淘天社招面问这条，考的是你能不能把产品里的「智能」拆开：哪些是离线 / 在线判别，哪些真要状态机。对齐后，评测也拆开：打分看校准与一致性，Agent 看任务成功、步数、越权率。不要用 Agent 评测套打分器，也不要把 RM 当 Agent。

## 追问

- **带一次工具的打分算不算？** 有反馈但无多步决策，更接近工具增强判别；看有没有 observe-act 循环和终止条件。
- **多轮对话就是 Agent 吗？** 不一定。多轮只是补槽的表单，没有工具与状态转移，仍是对话策略。
- **RM / Judge 是 Agent 吗？** 不是。它们是一次性评分函数，见 `data-reward-calibration`。
- **为何定义重要？** 权限、审计、评测都随回路变：打分器只读即可，Agent 必须有停止与确认。
