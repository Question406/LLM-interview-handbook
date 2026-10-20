---
id: jd-agent-vs-rag
section: agent
order: 166
level: A
title: 京东：Agent 和 RAG 的原理有何不同？
quick: "检索增强生成（RAG） 是「检索一块知识再生成」的单步或浅循环；Agent 是带状态的决策环，可多次选工具、改计划、拒答。RAG 常是 Agent 的一个工具，两者可以叠，不必二选一。"
tags:
  - JD
  - Agent
  - RAG
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 京东大模型算法 实习面经
    url: https://www.nowcoder.com/feed/main/detail/9ce9749030b24f6a9a7afcaa62b27f46
    type: candidate-first-hand
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“解释Agent和RAG原理”**

常见误区是：「Agent 就是更好的 RAG」。检索增强生成（RAG） 是检索一块知识再生成，目标是降低参数记忆造成的过时和幻觉；Agent 是带状态的决策环，可多次选工具、改计划、拒答。RAG 常常只是 Agent 动作集合里的一种。没有状态机和副作用控制，就只是 RAG 管道。场景选择见 `jd-agent-beyond-guide`，评测差异见 `jd-agent-eval-beyond-qa`。

## RAG：检索约束生成

主路径：query → 切块索引召回 →（可选重排）→ 拼上下文 → 生成，并尽量带引用。核心组件是切块、索引、召回、重排和引用约束。它解决的是「答案应来自某份文档」，管不了「去改库存」。循环若存在，也多是 query 改写或补检索，世界状态通常不因生成而改变。

电商里 SOP、类目规则、活动说明适合 RAG。实时库存、订单能否改址，文档里往往没有此刻的真值，硬用 RAG 会把过期表格念成事实。Memory 与 RAG 也不要合成一个库，字节侧分工见 `byte-rag-memory-context`。

## Agent：观察 → 动作 → 环境 → 再决策

Agent 维护任务状态：已查过的订单、未决的权限、下一步假设。动作可以是检索（RAG）、SQL、库存接口、工单 API，也可以是问用户或拒答。环境返回 Observation 后才能决定是否继续。终止条件、权限、重试属于 Harness，见 `agent-harness`。

和 Workflow 的差别：路径事先写得全、一致性要求高，用工作流；路径随观察变化，用 Agent，见 `meituan-workflow-vs-agent`。面试不要把任何带检索的聊天都叫 Agent。

## 用「客服问库存」对齐二者

纯 RAG：只能念「库存以页面为准」或过期 FAQ，不能给出当前可售量。Agent：调库存接口，再决定是否建议加购、是否转人工。若接口失败，按错误码恢复，别编造数字，见 `byte-tool-fail-retry`。

评测也不同。RAG 看 Recall@K、引用是否支撑答案、无答案是否拒答。Agent 还要看路由、工具选择、参数合法、无效调用和高风险保守性。把 Agent 只当 RAG 来测，会放过乱调工具但最后一句碰巧对的系统。原理上也可写成：RAG 近似 $p(\text{answer}\mid q, \text{docs})$；Agent 近似在工具与环境上的策略 $\pi(a\mid s)$，状态 $s$ 含尚未完成的目标和已发生副作用。缺 $s$ 的更新，就没有 Agent。

## 追问

- **多轮检索算 Agent 吗？** 若没有工具副作用、没有状态机，仍是 RAG 管道加深。分界是有没有「选动作、改世界、再观察」。
- **Agent 还要不要 RAG？** 要。文档型问题走检索工具，实时状态走业务 API。二者叠加，不是替换。
- **为什么内部更爱上 Agent？** 运营/售后要查实时单和写工单；纯导购话术有时 RAG 够用。按任务选，见 `jd-agent-beyond-guide`。
- **幻觉来源有何不同？** RAG 幻觉常是未引用或检索错；Agent 幻觉常是没调工具却假装调了，或把失败 Observation 说成成功。归因见 `jd-agent-reflection-error-attribution`。
