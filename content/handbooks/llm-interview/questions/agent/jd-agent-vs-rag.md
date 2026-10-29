---
id: jd-agent-vs-rag
section: agent
order: 166
level: A
title: 京东：Agent 和 RAG 的原理有何不同？
quick: >-
  检索增强生成（RAG）是先检索一块知识再生成，解决「答案要来自某份文档」；Agent
  是带状态的决策环，能多次选工具、改计划、拒答，动作还会改变外部世界。RAG 常是 Agent 的一个工具，两者可以叠加，不必二选一。
tags:
  - JD
  - Agent
  - RAG
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 京东大模型算法 实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/9ce9749030b24f6a9a7afcaa62b27f46'
    type: candidate-first-hand
---

## 真题记录

- 公司：京东
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“解释 Agent 和 RAG 原理”**

RAG 是检索一块知识再生成，目标是减少参数记忆带来的过时和 hallucination；Agent 是一个带状态的决策环，可以多次选工具、改计划、拒答，动作还会改变外部世界。RAG 常常只是 Agent 动作集合里的一种。没有状态机和副作用控制，就只是一条 RAG 管道，算不上「更好的 RAG」。

用「客服问库存」最容易看出区别。纯 RAG 只能念出「库存以页面为准」或者一份过期的 FAQ，给不出当前可售量。Agent 会去调库存接口，再决定要不要建议加购、要不要转人工；接口失败了就按错误码恢复，别编一个数字出来，见 `byte-tool-fail-retry`。

检索增强生成（RAG）的主路径是 query → 切块索引召回 →（可选重排）→ 拼上下文 → 生成，并尽量带引用，核心组件就是切块、索引、召回、重排和引用约束。它解决「答案应来自某份文档」，管不了「去改库存」。就算有循环，也多半是 query 改写或补检索，世界状态通常不会因为生成而改变。电商里的 SOP、类目规则、活动说明适合 RAG；实时库存、订单能不能改址，文档里往往没有此刻的真值，硬用 RAG 会把过期表格当事实念出来。Memory 和 RAG 也别合成一个库，字节侧的分工见 `byte-rag-memory-context`。

Agent 维护任务状态：查过哪些订单、哪些权限还没定、下一步的假设是什么。它的动作可以是检索（也就是 RAG）、SQL、库存接口、工单 API，也可以是问用户或拒答，环境返回 Observation 之后才决定要不要继续。终止条件、权限、重试这些属于 Harness，见 `agent-harness`。和 Workflow 的区别在路径上：事先写得全、一致性要求高，用工作流；路径随观察变化，用 Agent，见 `meituan-workflow-vs-agent`。所以面试时别把任何带检索的聊天都叫 Agent。

原理上也可以写成：RAG 近似 $p(\text{answer}\mid q, \text{docs})$；Agent 近似在工具与环境上的策略 $\pi(a\mid s)$，状态 $s$ 含尚未完成的目标和已发生副作用。缺 $s$ 的更新，就没有 Agent。评测也跟着不同。RAG 看 Recall@K、引用是否支撑答案、无答案时是否拒答；Agent 还要看路由、工具选择、参数合法、无效调用和高风险保守性。把 Agent 只当 RAG 来测，会放过乱调工具、最后一句碰巧答对的系统。

## 追问

**多轮检索算 Agent 吗？**
没有工具副作用、没有状态机的话，还是加深了的 RAG 管道。分界在于有没有「选动作、改世界、再观察」。

**有了 Agent 还要不要 RAG？**
要。文档型问题走检索工具，实时状态走业务 API，两者叠着用，谁也替换不了谁。

**为什么公司内部更爱上 Agent？**
运营和售后要查实时订单、写工单，纯导购话术有时 RAG 就够了。按任务选，见 `jd-agent-beyond-guide`。

**两者的 hallucination 来源有什么不同？**
RAG 的 hallucination 常是没引用或者检索错了；Agent 的 hallucination 常是没调工具却假装调了，或者把失败的 Observation 说成成功。归因见 `jd-agent-reflection-error-attribution`。

相关：`jd-agent-beyond-guide`、`jd-agent-eval-beyond-qa`
