---
id: meituan-langgraph-vs-prompt
section: agent
order: 161
level: A
title: 美团北斗：LangGraph 做多轮 Agent，比手写 prompt 流程强在哪？
quick: "图把状态、边、断点和重试写成可序列化控制流，失败可从节点恢复；手写 输入提示（prompt） 链把控制藏在文本里，难测、难回放。效果优势来自状态机约束，不是框架品牌。"
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

常见误区是：背框架名，列出 checkpoint、reducer、studio 就算答完。北斗问的是工程和效果优势从哪来：状态机约束，不是品牌。手写「再拼一段 prompt 再调一次」把分支、循环、记忆都塞进字符串，日志对不齐，断点续跑只能重来。LangGraph 一类把节点和边写成图，state 可序列化；简单 FAQ 不必上图。和 `meituan-workflow-vs-agent` 一致：图可以是死 Workflow，也可以把下一跳交给模型。

## 工程：可序列化控制流，别藏在文本里

手写 输入提示（prompt） 链的控制流在模型输出里：下一段叫什么工具、要不要澄清，下一轮只能靠复读历史猜测。出了问题难指到「哪条边」。图把调用模型 / 工具 / 人审做成节点，边写条件、超时、重试、降级。state 可 checkpoint，失败从节点恢复而不是整段对话重跑。单节点可单测：给定 state 断言下一跳和工具参数，不必每次打真模型。按边回放便于对客诉复盘。

权限挂在工具节点，别靠 system prompt「请不要退款」。多轮里用户改地址、改人数，状态字段版本化，避免 输入提示里同时出现新旧值。这是 harness 该做的，见 `agent-harness`。代价是图会变重：节点一多，改一条边要回归整图；所以稳定 SOP 先画小图，开放探索再把个别节点交给模型选边。

## 效果优势来自约束，换框架不会自动更聪明

效果上，强约束链路少跑飞：退款必须先查订单再进人审，模型无法跳步。评测能按节点看瓶颈，卡在检索还是卡在澄清。手写链只能看最终回复，归因回到「再调一下 prompt」。多轮记忆若只靠窗口拼接，会丢槽位；图的 state 把订单号、门店、配送状态做成字段，和 `meituan-memory-vs-rag` 的记忆职责一致。

不要承诺「上了 LangGraph 幻觉就少」。幻觉仍要检索与忠实层，见 `jd-rag-hallucination-fallback`。框架只保证走哪条边、状态是否可恢复。工程优势是可恢复、可测、权限可挂边；效果来自少让模型自由发挥控制流。简单检索问答用手写链更便宜。北斗业务里多轮常常夹着门店、人数、配送时间这些槽位，手写链最容易在第三轮把旧地址和新地址同时喂给模型。图把槽位做成 state 字段，边条件写「地址未确认则进人审 / 澄清」，少一次静默用错槽。迁移时先把现有 prompt 链里已经稳定的分支抽成节点，开放探索仍留一个 Agent 节点，避免一夜重写成大图。

## 追问

- **图一定比 prompt 效果好吗？** 不一定。FAQ 和单跳 检索增强生成（RAG） 上图只增加跳转成本。优势出现在有分支、重试和人审的多轮。
- **下一跳交给模型还算 LangGraph 的优势吗？** 算工程优势（仍有 state 和权限），但效果上已接近 Agent，方差会变大，见 `meituan-workflow-vs-agent`。
- **checkpoint 能解决幻觉吗？** 不能。它解决的是失败恢复和回放，不解决无依据断言。
- **自己画状态机、不用 LangGraph 行不行？** 行。要的是图 + 可序列化 state，框架可替换。
