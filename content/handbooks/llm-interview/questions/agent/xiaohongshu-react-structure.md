---
id: xiaohongshu-react-structure
section: agent
order: 148
level: A
title: 小红书：了解 ReAct 结构吗？
quick: >-
  ReAct 交替 Thought / Action / Observation：先推理再调工具，把环境反馈写回上下文。它是策略骨架，不是训练算法；要补循环上限、解析器和可回放日志才能上线。
tags:
  - Xiaohongshu
  - ReAct
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 小红书大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/3f96f6fe7ed44c3b8c49cea3455d38a4
    type: candidate-first-hand
  - title: ReAct — Synergizing Reasoning and Acting in Language Models
    url: https://arxiv.org/abs/2210.03629
    type: primary
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“了解ReAct结构吗，介绍一下?”**

错法：把任何 Agent 都叫 ReAct。没有显式 Thought 或没有环境反馈，只是 function calling 循环。ReAct（Yao et al.）把「只想」和「只做」拼起来：Thought 决定假设与下一步，Action 调用检索 / 工具，Observation 把结果接回，再进入下一轮，直到给出最终答案。它是策略骨架，不是训练算法。多轮检索何时停，见 `xiaohongshu-deep-research-stop`。

## Thought / Action / Observation

比纯 CoT 多了外部证据，比纯 tool-call 多了可检查的中间理由。Action 必须可解析（名字 + 参数），Observation 是环境事实，不应被模型改写成「我认为成功了」。循环要有终止：最终答案、硬预算或校验失败。校验层决定哪一跳能往下走，商汤那题把这一层说成最重要，见 `sensetime-agent-three-modules`。Thought 对用户是否可见是产品决策：内部审计要留，对 C 可能只展示行动摘要。

## 上线必须补的工程

生产不能只复述论文三元组。要补：Action 解析失败怎么办、最大步数、Observation 过长如何摘要、工具超时 / 空结果如何重试、日志是否可回放。训练或 SFT 时要对齐这三块的 schema，别只拟合最终答案。Observation 进上下文会迅速涨 token，压缩顺序见 `pdd-context-overflow`。权限和副作用不能写在 Thought 里「注意安全」，要在工具层强制。

## 和 function calling、多 Agent 的界限

现代 API 的 tool call 可以没有自然语言 Thought，仍是 ReAct 的亲戚：模型选动作、环境返回、再决策。差别在于：ReAct 论文强调可检查的推理痕迹；生产可以结构化 Thought。没有环境反馈的多步自说自话不是 ReAct。多 Agent 只是把某些 Action 交给另一个策略，协作协议见 `pdd-multi-vs-single-agent`。LangGraph、MCP、Skill 不是 ReAct，那些是图、协议和操作知识，见 `xiaohongshu-mcp-skill-token-efficiency`。介绍时按循环画一遍，再补工程补丁。

## 追问

- **没有 Thought 还叫 ReAct 吗？** 严格说不是。那是 tool-call 循环；可以说同源，不要硬套名字。
- **Thought 要不要给用户看？** 内部要留日志；对 C 看产品，避免把未验证假设展示成结论。
- **和 CoT 的本质差别？** CoT 不接触环境；ReAct 每步把 Observation 写回，证据来自工具。
- **死循环怎么防？** 硬步数、重复 Action 检测、空 Observation 熔断，见 `xiaohongshu-deep-research-stop`。
