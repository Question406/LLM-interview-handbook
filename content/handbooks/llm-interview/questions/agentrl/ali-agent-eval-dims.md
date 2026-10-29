---
id: ali-agent-eval-dims
section: agentrl
order: 17
level: S
title: Agent 评估体系有哪些维度？如何衡量 planning vs hallucination？
quick: >-
  我会分维度报：任务成功率、步数和成本、工具正确率、规划、hallucination / 忠实度、安全越权率、该澄清却没问的比例。Planning
  看关键动作覆盖和依赖顺序，违反硬依赖就算失败；hallucination 看无证据断言和编出来的 tool
  参数。两者修法不同，混成一个成功率就分不清该修哪层。
tags:
  - Alibaba
  - Agent
  - Eval
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

我会把评估拆成几维分开报：任务成功率、步数和成本、工具正确率、规划质量、hallucination / 忠实度、安全越权率，再加一个该澄清却没问的比例。planning 失败和 hallucination 都会让成功率掉，但修法完全不同：前者是子目标或依赖拆错了，后者是没有证据就下断言，或者编了 tool 参数。混成一个总分，就判断不了线上该修规划还是证据使用，原因也没法复现。

举个淘天的退货场景。一条轨迹没查订单就直接发起退款，碰巧退成功了，成功率记一次成功，可「先查单再退款」这个硬依赖被违反了，这算 planning fail。另一条轨迹顺序都对，订单号却是模型编的，这是 hallucination。两个问题都落在同一个成功率里，下周你只会看到 success 掉了几个点。

## 结果和过程分开评

最终结果看任务完成和业务 KPI，比如退货成功、改址生效、客诉关闭；过程看平均工具轮次、无效调用、循环率、超时和重试。只优化结果，模型会学会碰巧成功，漏了步骤但下游碰巧过了；只优化过程（少步、少调用），又会鼓励过早结束。成本也要记，同样成功，10 次工具调用和 2 次是两种策略。复现靠固定评测集加 trace 回归，人工抽检只拿来 calibration，不当主指标。单次 LLM 打分也算不上 Agent 评估，对照 `ali-score-vs-agent`。

Planning 看的是能不能执行，文采不算。我会看子目标有没有覆盖关键步骤、依赖顺序对不对、有没有过早结束、计划能不能被工具执行（字段和类型规范（schema）填得上、权限够）。具体做法是把 gold plan 拆成必须命中的关键动作集合，算覆盖率；像「先查单再退款」这种硬依赖，违反了就判 planning fail，哪怕最后退成功了。该问地址却直接猜，记进澄清率，这是规划偷懒，和 hallucination 分开算。模块化规划和 fallback 见 `ali-modular-agent-plan`。

hallucination 看三件事：无依据的事实、伪造的引用、和工具结果矛盾。Agent 里最常见的是错误 tool 参数（编订单号、编原因码），以及无视 observation 继续编。忠实度要对齐「当前工具返回 + 允许的知识库」，预训练记忆不算证据。这和检索增强生成（RAG）评估是同一个结构：证据一层、生成忠实一层、端到端一层，见 `ali-rag-eval`、`ali-hallucination-intercept`。没有证据就该拒答或澄清，拒答率低得反常，通常是 hallucination 被 success 掩盖了。安全单独开一维，越权、不可逆操作没确认，这些要是算进 hallucination，Guardrail 和事实核对会修错 acceptance checks。

## 收成一张表

最后我会收成一张表：行是最终结果 / Process / Planning / Faithfulness / Safety，列是「能不能自动算、金标从哪来、失败时修哪一层」。没有金标 plan 就别假装算 planning F1，改成关键动作覆盖；没有证据文档就别假装算引用正确率。Agent RL 训练用的奖励分数（reward），比如 GRPO 组内的 $A$、DPO 的偏好，也替代不了这张表，训练信号会被 hack，评估集要独立、可回放。新失败 trace 入库时，要能指出它是规划依赖错、工具参数 hallucination，还是越权。

## 追问

**全交给 LLM-as-judge 行不行？**
不行。Judge 自己会 hallucination，还偏好长回复。关键动作覆盖、schema 校验、和 observation 是否矛盾，这些要规则化，Judge 只评开放表述。

**Planning 怎么和 ReAct 轨迹对齐？**
按 tool-call boundaries 切段，对 gold 关键步骤做集合覆盖，别对整段 Thought 算 BLEU。

**线上怎么回归？**
固定 trace 回放，加上新失败 case 入库。主观感觉变好不算通过。
