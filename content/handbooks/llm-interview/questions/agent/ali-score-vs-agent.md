---
id: ali-score-vs-agent
section: agent
order: 24
level: A
title: 单次 LLM 打分算不算 Agent？和多轮工具 Agent 的核心区别？
quick: "单次 LLM 打分接收固定输入、输出分数就结束，不算 Agent。Agent 会根据工具或环境返回的结果更新状态、决定下一步，并在满足条件时停止，判断时看有没有这个决策循环。"
tags:
  - Alibaba
  - Agent
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---

单次 LLM 打分不算 Agent，区别在控制回路，跟用没用 LLM、调没调过一次 function calling 都没关系。打分器拿到固定输入，输出一个分数或标签就结束，更像一次性推理或判别；Agent 是 observe → act → observe 的循环，工具、用户或环境会改变 state，系统据此决定下一步，并且有终止条件。面试时我会先和面试官把这个定义对齐，免得各说各的。

举个例子：用 LLM 给商品评论打 1 到 5 分，不再查库存、不再问用户，这是打分器。同一个模型如果先查订单，再决定要不要调退货工具，等用户确认后才提交，这才是 Agent。讲 Agent 时要说清它的状态、动作空间、停止条件和责任边界。

容易混淆的是带一次工具的情况。先搜政策再打「是否可退」，有了环境反馈，但如果没有多步决策和终止策略，它更接近工具增强的判别。判断标准是有没有循环：会不会根据新观察改变下一步，会不会再问、再调、再停。Skill、Memory、检索增强生成（RAG）本身也不等于 Agent 回路，见 `ali-skill-memory-rag`；规划和状态机见 `ali-modular-agent-plan`。

定义之所以重要，是因为权限、审计和评测都随回路变。打分器通常只读就够，Agent 却可能对同一订单调两次退款，必须有停止和确认。把一次 FC 也叫 Agent，后续安全评审就会漏掉循环里的重复执行和权限升级，所以权限和 HITL 要按「会不会形成回路」来升级，见 `ali-guardrail`、`ali-hitl-risk`。评测也拆开：打分器看校准和一致性，Agent 看任务成功、步数、越权率，别用 Agent 的评测去套打分器。淘天社招面问这条，考的就是能不能把产品里的「智能」拆开，分清哪些是离线或在线判别，哪些真的需要状态机。

## 追问

**多轮对话就是 Agent 吗？**
不一定。只是补槽的多轮表单，没有工具和状态转移，仍然是对话策略。

**奖励模型（RM）或 Judge 是 Agent 吗？**
不是。它们是一次性的评分函数，见 `data-reward-calibration`。
