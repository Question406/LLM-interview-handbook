---
id: ali-agent-eval-dims
section: alibaba
order: 17
level: S
title: Agent 评估体系有哪些维度？如何衡量 planning vs hallucination？
quick: >-
  任务成功率、步数/成本、工具正确率、规划遵从、幻觉/忠实度、安全越权率、澄清率。Planning 看子目标分解与依赖；幻觉看无证据断言与错误 tool
  参数。
tags:
  - Alibaba
  - Agent
  - Eval
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

陷阱是只报「任务成功率」。淘天 Agent 面里，planning 失败和 hallucination 都会让 success 掉，但修法完全不同：前者是子目标/依赖拆错，后者是无证据断言或伪造 tool 参数。糊成一个数，线上只能靠聊天感觉，回不去。单次 LLM 打分也不是 Agent 评估（对照 `ali-score-vs-agent`）。

## Outcome 与 Process 必须拆开

Outcome 看任务完成和业务 KPI（退货成功、改址生效、客诉关闭）。Process 看平均工具轮次、无效调用、循环率、超时与重试。只优化 Outcome，模型会学会「碰巧成功」：漏步骤但下游碰巧过。只优化 Process（少步、少调用）会鼓励过早结束。固定评测集 + trace 回归才能复现；人工抽检只当校准，不当主指标。淘天场景还要记成本：同样成功，10 次工具调用和 2 次不是同一策略。

## Planning：可执行性，不是文采

Planning 看子目标是否覆盖关键步骤、依赖顺序对不对、是否过早结束、计划是否可被工具执行（schema 可填、权限够）。不要用「计划写得像不像」当指标。可落地做法：把 gold plan 拆成必须命中的关键动作集合，算覆盖率；对「先查单再退款」这类硬依赖，违反则判 planning fail，即使最终退成功。澄清率也要记：该问地址却直接猜，是规划偷懒，不是幻觉。模块化规划与 fallback 见 `ali-modular-agent-plan`。

## Hallucination：无证据断言 vs 错参

幻觉看三件事：无依据事实、伪造引用、与工具结果矛盾。Agent 里最常见的是错误 tool 参数（编订单号、编原因码）和无视 observation 继续编。忠实度应对齐「当前工具返回 + 允许的知识库」，不是对齐预训练记忆。这和 RAG 评估同构：证据一层、生成忠实一层、端到端一层（见 `ali-rag-eval`、`ali-hallucination-intercept`）。无证据必须拒答或澄清；拒答率过低，通常是幻觉被 success 掩盖。Safety 单独开一维：越权、不可逆未确认，不要把安全失败算进 hallucination，否则 Guardrail 和事实核对会修错闸门。

淘天白板可以收成一张表：行是 Outcome / Process / Planning / Faithfulness / Safety，列是「自动可算吗、金标从哪来、失败时修哪一层」。没有金标 plan 就不要假装算 planning F1，改成关键动作覆盖；没有证据文档就不要假装算引用正确率。Agent RL 的训练 reward（GRPO 组内 $A$、DPO 偏好）更不能替代这张表——训练信号会 hack，评估集必须独立、可回放。新失败 trace 入库后要能指出是规划依赖错、工具参数幻觉，还是越权，否则下周还是只看到 success 掉了几个点。

## 追问

- **为什么不能只用 LLM-as-judge？** Judge 自己会幻觉，且偏好长回复。关键动作覆盖、schema 校验、与 observation 矛盾必须规则化；Judge 只评开放表述。
- **Planning 和 ReAct 轨迹怎么对齐？** 按 tool-call 边界切段，对 gold 关键步骤做集合覆盖，不要对整段 Thought 做 BLEU。
- **线上怎么回归？** 固定 trace 回放 + 新失败 case 入库。感觉变好不算过。
