---
id: ali-mcp-vs-fc
section: agent
order: 25
level: S
title: MCP 和 Function Calling 的区别？为何生产不能只靠 FC？
quick: "Function Calling 让模型表达要调用哪个函数及其参数；MCP 则规定工具、资源和提示怎样被发现、连接与复用。二者可以一起使用。生产系统还需要注册、鉴权、版本和审计，MCP 提供连接协议，但不会自动完成授权。"
tags:
  - Alibaba
  - MCP
  - Tool
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 阿里 AI 应用开发面经 MCP
    url: 'https://www.nowcoder.com/discuss/877584799056023552'
    type: legacy-reference
---

常见误区是：MCP 是「更好的 Function Calling」，或反过来觉得有了 FC 就不需要协议。FC 是模型侧的接口形态：应用在请求中提供工具 schema，模型返回结构化调用，宿主负责执行。MCP 是连接协议：把能力抽象为可发现的 tools / resources / prompts，统一 schema、传输与会话，让多个 Agent、IDE、模型复用同一套服务。生产要的是协议层与业务层解耦，业务各自复制工具描述，容易造成版本和治理不一致。边界见 `jd-mcp-protocol`、`mcp-tool-catalog-trust`。

## FC 是模型侧接口，MCP 是连接协议

Function Calling 解决「模型怎么表达我要调哪个函数、参数是什么」。宿主负责拼 schema、解析调用、真正执行、把结果写回上下文。换一个模型供应商，schema 方言、并行调用、拒绝调用的语义都可能变。MCP 解决「工具怎么被发现、连上、复用」：Client / Host 与 Server 先协商能力，再 `tools/list`、`tools/call`；传输可以是 stdio 或 Streamable HTTP。模型仍然可以走 FC 来选工具，但工具目录、鉴权入口、日志字段不再绑死在某一个 chat completions 请求里。

可以记成：FC 是对话 API 上的调用语法；MCP 是工具进程与宿主之间的 RPC 会话。前者回答「这次生成出什么 JSON」，后者回答「这个能力谁提供、如何握手、结果怎么回写」。

## 生产为什么不能只靠 FC

只靠 FC 时，每个业务在自己的 输入提示里复制一份工具描述，权限难管、日志不统一、难以跨团队复用。淘天 / 阿里应用开发面常追问的是：工具一多，schema 分裂、版本对不齐、审计对不上人。大厂更在意协议层：同一支付工具既能给客服 Agent 用，也能给 IDE Agent 用，白名单和审计挂在网关，而不是散落在各模型请求里。Skill 是「这类任务怎么做」，MCP 是「能力怎么连」。不要把操作手册塞进 检索增强生成（RAG） 就当有协议，见 `ali-skill-memory-rag`。

## 协议层不等于权限层

MCP 统一怎么连、怎么发现，不自动授权。Server 自称只读不能当授权；执行前仍要在 Host 做身份、参数和副作用校验。高风险工具的确认、金额上限、SQL 约束仍在策略引擎，见 `ali-guardrail`。把 MCP 当成安全方案，是面试里最常见的越级。

## 追问

- **没有 MCP 能不能生产？** 能，但要自建工具注册、鉴权、观测；人一多就会长成内部 MCP。
- **MCP 替换 FC 吗？** 不替换。模型选工具仍常走 FC / tool schema；MCP 管连接与复用。
- **传输选 stdio 还是 HTTP？** 本地 IDE 常用 stdio；多租户服务用 HTTP。通道不是权限模型。
- **工具描述放哪？** 协议侧可发现，模型侧只暴露当前任务相关的一小撮，避免 schema 爆炸。见 `agent-schema-contract`。
