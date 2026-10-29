---
id: xiaohongshu-react-structure
section: agent
order: 148
level: A
title: 小红书：了解 ReAct 结构吗？
quick: >-
  了解。ReAct 让模型交替做 Thought / Action /
  Observation：先想下一步，再调工具，把环境返回写回上下文，循环到给出答案。它是策略骨架，本身不带训练算法；要上线，还得补循环上限、解析器和可回放日志。
tags:
  - Xiaohongshu
  - ReAct
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 小红书大模型实习一面
    url: 'https://www.nowcoder.com/feed/main/detail/3f96f6fe7ed44c3b8c49cea3455d38a4'
    type: candidate-first-hand
  - title: ReAct — Synergizing Reasoning and Acting in Language Models
    url: 'https://arxiv.org/abs/2210.03629'
    type: primary
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“了解 ReAct 结构吗，介绍一下?”**

了解。ReAct 让模型在一个循环里交替做三件事：Thought 写下当前的判断和下一步打算，Action 调一个检索或工具，Observation 把工具返回的结果接回上下文，然后进入下一轮，直到给出最终答案。它是一种策略骨架，本身不带训练算法；要上线，还得补循环上限、解析器和可回放日志。

举个例子，用户问「这两款面霜哪个更适合敏感肌」。模型先想「我需要两款的成分表」，这是 Thought；调检索去拿成分，这是 Action；检索结果回来，这是 Observation；它再想「A 里有酒精，还得查一下 B 有没有香精」，进入下一轮。Yao et al. 的 ReAct 就是把「只想」的 chain of thought（CoT，即分步推理过程）和「只做」的工具调用拼在一起：比纯 CoT 多了外部证据，比纯 tool-call 多了可检查的中间理由。所以常见的误区是把任何 Agent 都叫 ReAct。没有显式 Thought，或者没有环境反馈，那只是 function calling 循环。

三块各有约束。Action 要能解析，也就是名字加参数；Observation 是环境事实，模型不该把它改写成「我认为成功了」；循环要有终止条件，比如给出最终答案、碰到硬预算、或者校验失败。校验层决定哪一跳能往下走，商汤那题把这一层说成最重要，见 `sensetime-agent-three-modules`。Thought 给不给用户看是产品决策：内部审计要留，对 C 可能只展示行动摘要。

上线时论文里的三元组只是起点。还要想清楚 Action 解析失败怎么办、最大步数设多少、Observation 太长怎么摘要、工具超时或返回空结果怎么重试、日志能不能回放。Observation 进上下文以后 token 涨得很快，压缩顺序见 `pdd-context-overflow`。权限和副作用要在工具层强制，在 Thought 里写一句「注意安全」起不了作用。训练或 SFT 时，三块都要对齐字段和类型规范（schema），别只拟合最终答案。

## 和 function calling、多 Agent 的界限

现代 API 的工具调用可以没有自然语言 Thought，它仍然是 ReAct 的亲戚：模型选动作、环境返回、再决策。区别在于 ReAct 论文强调可检查的推理痕迹，生产里可以把 Thought 结构化。没有环境反馈、多步自说自话的，不算 ReAct。多 Agent 只是把某些 Action 交给另一个策略，协作协议见 `pdd-multi-vs-single-agent`。LangGraph、MCP、Skill 分别是图、协议和操作知识，和 ReAct 不在一个层面，见 `xiaohongshu-mcp-skill-token-efficiency`。面试时我会按循环画一遍，再讲这些工程补丁。

## 追问

**没有 Thought 还叫 ReAct 吗？**
严格说不叫。那是 tool-call 循环，可以说两者同源，别硬套名字。

**Thought 要不要给用户看？**
内部日志一定要留；对 C 看产品需要，避免把没验证过的假设当结论展示出来。

**和 CoT 的本质差别是什么？**
CoT 不接触环境；ReAct 每一步都把 Observation 写回，证据来自工具。

**死循环怎么防？**
硬步数上限、重复 Action 检测、空 Observation 熔断。多轮检索什么时候停，见 `xiaohongshu-deep-research-stop`。
