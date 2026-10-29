---
id: ali-mcp-vs-fc
section: agent
order: 25
level: S
title: MCP 和 Function Calling 的区别？为何生产不能只靠 FC？
quick: >-
  假设聊天助手要查询公司订单。Function Calling 让模型表达“调用哪个工具、参数是什么”；MCP
  则提供工具服务如何连接、发现和交换请求结果的协议；Agent framework 组织调用前后的状态与执行流程。
tags:
  - Alibaba
  - MCP
  - Tool
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: ↗ 阿里 AI 应用开发面经 MCP
    url: 'https://www.nowcoder.com/discuss/877584799056023552'
    type: legacy-reference
---

## 回答思路

> **问题与场景：** 假设聊天助手要查询公司订单。
>
> **做法与原因：** 三者可以一起使用。
>
> **检查与取舍：** 我会用一次真实的查询或写操作说明各自负责哪一步，再讨论是否需要某个 framework。

## 可以这样回答

假设聊天助手要查询公司订单。Function Calling 让模型表达“调用哪个工具、参数是什么”；MCP 则提供工具服务如何连接、发现和交换请求结果的协议；Agent framework 组织调用前后的状态与执行流程。

三者可以一起使用。模型先提出调用，运行程序检查权限，再通过工具连接取得结果，最后把结果交给模型。连接协议不会自动决定用户有权做什么。

我会用一次真实的查询或写操作说明各自负责哪一步，再讨论是否需要某个 framework。只列框架名，解释不了失败后在哪里重试、授权由谁检查。

## 技术备查

Function Calling 解决模型怎么表达「我要调哪个函数、参数是什么」，MCP 解决工具怎么被发现、连上和复用，两者在不同的层，可以一起用。所以把 MCP 说成「更好的 Function Calling」，或者觉得有了 FC 就不需要协议，都答偏了。可以这么记：FC 是对话 API 上的调用语法，回答「这次生成出什么 JSON」；MCP 是工具进程和宿主之间的 RPC 会话，回答「这个能力谁提供、怎么握手、结果怎么回写」。

FC 的流程是应用在请求里提供工具 schema，模型返回结构化调用，宿主负责拼 schema、解析调用、真正执行，再把结果写回上下文。换一家模型供应商，schema 方言、并行调用、拒绝调用的语义都可能变。MCP 把能力抽象成可发现的 tools / resources / prompts，统一 schema、传输和会话：Client / Host 和 Server 先协商能力，再走 `tools/list`、`tools/call`，传输可以是 stdio 或 Streamable HTTP。模型选工具时仍然可以走 FC，但工具目录、鉴权入口、日志字段不再绑死在某一个 chat completions 请求里。

生产上只靠 FC 的麻烦在于，每个业务都在自己的 prompt 里复制一份工具描述，权限难管、日志不统一，也很难跨团队复用。淘天和阿里应用开发面常追问的就是这个：工具一多，schema 分裂、版本对不齐、审计对不上人。比如同一个支付工具，既给客服 Agent 用，也给 IDE Agent 用，白名单和审计应该挂在网关上，散在各个模型请求里就管不住。所以大厂更在意协议层，让协议层和业务层解耦。顺带分一下，Skill 讲「这类任务怎么做」，MCP 讲「能力怎么连」，把操作手册塞进检索增强生成（RAG）不等于有了协议，见 `ali-skill-memory-rag`。

还要讲清 protocol responsibilities 与 authorization rules。MCP 统一了怎么连、怎么发现，但不会自动授权。Server 自称只读不能当作授权，执行前 Host 仍要做身份、参数和副作用校验；高风险工具的确认、金额上限、SQL 约束都 on-policy 引擎里，见 `ali-guardrail`。把 MCP 当成安全方案，是面试里最常见的越级。更详细的 authorization rules 见 `jd-mcp-protocol`、`mcp-tool-catalog-trust`。

## 追问

**没有 MCP 能上生产吗？**
能，但要自建工具注册、鉴权和观测，人一多，最后就长成了一套内部 MCP。

**MCP 会替代 FC 吗？**
不会。模型选工具仍常走 FC / tool schema，MCP 管连接和复用。

**传输选 stdio 还是 HTTP？**
本地 IDE 常用 stdio，多租户服务用 HTTP。通道只是通道，和权限模型是两件事。

**工具描述放在哪？**
协议侧负责可发现，模型侧只暴露当前任务相关的一小撮，避免 schema 爆炸，见 `agent-schema-contract`。
