---
id: meituan-langgraph-vs-prompt
section: agent
order: 161
level: A
title: 美团北斗：LangGraph 做多轮 Agent，比手写 prompt 流程强在哪？
quick: "优势来自把多轮控制流写成图：状态、边、断点和重试都可序列化，失败能从节点恢复，单个节点能测、能回放。手写 prompt 链把分支和记忆藏在文本里，难测也难复盘。效果上的提升来自状态机约束，换框架本身不会让模型更聪明，简单 FAQ 用手写链更便宜。"
tags:
  - Meituan
  - LangGraph
  - Agent
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团北斗大模型面试
    url: https://www.nowcoder.com/discuss/914814345970782208
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：北斗；大模型
- 届别 / 流程：原帖未披露
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“用 LangGraph 实现多轮对话 Agent,相比手写 prompt 流程有哪些工程和效果优势?”**

LangGraph 的优势主要来自状态机约束，框架品牌本身带不来什么。它把节点、边和 state 显式写出来，state 可以序列化，失败能从某个节点恢复，每个节点能单测、能回放；手写「再拼一段 prompt 再调一次」，会把分支、循环和记忆都塞进字符串，出了问题很难指到是哪条边。所以只列出 checkpoint、reducer、studio 这些名词不算答完，要讲清优势从哪来。

拿北斗这类多轮业务举例，对话里常夹着门店、人数、配送时间这些槽位。用户先说送到公司，后来改成送到家，手写链最容易在第三轮把旧地址和新地址同时喂给模型，模型挑错一个，就是一次静默用错槽。用图来做，槽位是 state 里的字段，改口时字段版本化，边条件写「地址未确认则进人审 / 澄清」，prompt 里就不会同时出现新旧值。

工程上，手写链的控制流在模型输出里：下一段叫什么工具、要不要澄清，下一轮只能靠复读历史猜，日志也对不齐，断点续跑只能整段重来。图把调用模型、调用工具、人审都做成节点，边上写条件、超时、重试和降级；state 可以 checkpoint，失败从节点恢复，不用整段对话重跑。单个节点可以单测，给定 state，断言下一跳和工具参数，不必每次打真模型；出了客诉，可以按边回放复盘。权限挂在工具节点上，别靠 system prompt 写一句「请不要退款」。这些都是 harness 该做的事，见 `agent-harness`。

效果上，强约束的链路少跑飞，比如退款必须先查订单再进人审，模型没法跳步。评测能按节点看瓶颈，看是卡在检索还是卡在澄清；手写链只能看最终回复，归因最后都回到「再调一下 prompt」。多轮记忆如果只靠窗口拼接会丢槽位，图的 state 把订单号、门店、配送状态做成字段，这和 `meituan-memory-vs-rag` 里记忆的职责一致。

不过我不会承诺「上了 LangGraph hallucination 就少」。框架只保证走哪条边、状态能不能恢复，hallucination 还是要靠检索与忠实层，见 `jd-rag-hallucination-fallback`。图也有代价：节点一多，改一条边要回归整张图；简单 FAQ 和检索问答不必上图，手写链更便宜。图可以是写死的 Workflow，也可以把下一跳交给模型，这和 `meituan-workflow-vs-agent` 的划分一致。迁移时我会先把现有 prompt 链里已经稳定的分支抽成节点，开放探索仍留一个 Agent 节点；稳定 SOP 先画小图，别一夜之间重写成大图。

## 追问

**图一定比 prompt 效果好吗？**
不一定。FAQ 和单跳检索增强生成（RAG）上图，只是多了跳转成本。优势出现在有分支、重试和人审的多轮任务里。

**下一跳交给模型，还算 LangGraph 的优势吗？**
工程上还算，state 和权限都还在；效果上已经接近 Agent，方差会变大，见 `meituan-workflow-vs-agent`。

**checkpoint 能解决 hallucination 吗？**
不能。它解决失败恢复和回放，管不了无依据的断言。

**自己画状态机、不用 LangGraph 行不行？**
行。要的是图加可序列化的 state，框架可以替换。
