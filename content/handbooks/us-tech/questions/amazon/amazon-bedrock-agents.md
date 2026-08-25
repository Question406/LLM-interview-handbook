---
id: amazon-bedrock-agents
section: amazon
order: 12
level: A
title: Amazon：Bedrock Agents 的工具、记忆、护栏，和自建 harness 怎么选？
quick: >-
  Agents 托管编排：Action Group 调 API / Lambda，Knowledge Base 做 RAG，Memory
  跨会话摘要，Guardrails 拦输入输出。自建 harness 换来重试、确认框、预算和沙箱的控制权。新账号公开方向是
  AgentCore；Classic 仍要能讲清循环。工具输出当不可信输入。
tags:
  - Amazon
  - Bedrock
  - Agents
  - Tools
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Automate tasks in your application using AI agents
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html
    type: primary
  - title: How Amazon Bedrock Agents work
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html
    type: primary
  - title: Retain conversational context across sessions using memory
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-memory.html
    type: primary
  - title: Detect and filter harmful content with Amazon Bedrock Guardrails
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html
    type: primary
---

Bedrock 应用岗把 agent 问成所有权题：谁调 API、记忆存在哪、拦了谁负责。公开文档里 Classic Agents 编排 FM、数据源和会话，Action Group 用 OpenAPI 或 function schema，可接 Lambda 或把控制交回应用。Memory 把跨 session 的对话收成摘要，按你给的 `memoryId` 加载。Guardrails 仍走输入 / 输出两道，见 `amazon-guardrails`。文档也写了 Classic 对 **新客户关闭**，新能力看 AgentCore。面试两套都要能讲，不要假装只有一个产品名。不是某次逐字真题。通用 harness 原则见 `design-agent-harness`。

## 托管循环里有什么，没有什么

一次 `InvokeAgent` 公开路径大致是：理解用户 → 决定调哪个 action 或查哪个 KB → 填参、调 Lambda 或 return control → 观察结果 → 再想一步 → 后处理。你可以改预处理 / 编排 / KB / 后处理的 prompt 模板，用 trace 看每步 rationale。这很像「少写编排代码」。

它 **不替你做** 的，才是和自建的分界：

- **工具权限和副作用。** Schema 能描述参数，不能描述「退款超过限额要人工」。不可逆动作要确认框或 return control，让应用层拍板，不要让模型直接打生产 Lambda。
- **预算。** 步数、token、墙钟、重试。托管循环会转，直到模型说结束或你超时。没有硬顶就会在工具抖动时空转。
- **沙箱。** Lambda 是你的运行时：VPC、IAM、密钥、出网。Agent 不管 kernel。工具 stdout / 网页 / PDF 都是不可信输入，进下一轮 prompt 前要截断、当数据不当指令。
- **记忆。** 文档：默认同 session；打开 memory 后，在 `endSession` 或 idle 超时后异步摘要，按 `memoryId` 存最多可到 365 天。摘要会丢细节、也会把不该长期记的 PII 写进去。用户级隔离是你传对 id；多用户共用一个 memoryId 就是串话。删记忆是产品功能，不是「模型会忘」。

Knowledge Base 是 RAG 插件，不是另一套接地契约。引用、过期条款、混合检索仍要你设计，见 `amazon-bedrock-rag`、`amazon-kendra-hybrid`。Agent 只是会在编排里决定何时去查。

Guardrails 挂到 agent 上：输入拦越狱和拒答主题（省一次编排），输出拦幻觉 / PII。Contextual grounding 仍只对输出有意义。流式和首 token 的冲突同 `amazon-p99-stream`。

## 何时用托管，何时自建

我会按控制权选：

- **托管 Agents / AgentCore。** 工具少而稳、API 已有 OpenAPI、要快速上内部助手、审计用 trace 就够。换模型时策略仍在 Guardrails 和应用 IAM。
- **自建 harness。** 要多步事务、补偿、人工确认、精细重试、和内部工作流引擎对接、或必须在工具之间做确定性状态机。模型只出结构化调用，循环在你的代码里。
- **混合。** 只读查询走托管；下单、改地址、退款 return control 回自己的服务。这往往是生产默认。

评测不要报「对话像不像人」。报：任务成功（工单是否解）、错误工具调用率、不该调而调（权限）、步数分布、记忆串话、Guardrail 漏拦 / 误拦。离线用带金标工具轨迹的 case；线上用升级工单和事故。Learn and Be Curious 是把失败轨迹写回评测，不是换更大 Nova，见 `amazon-nova`、`amazon-titan-eval`。

错法：把 OpenAPI 一贴就当安全；记忆当用户画像无限写；用 agent 替代政策引擎（Automated Reasoning / 规则仍要在工具层）；忽略 Classic vs AgentCore 的产品状态，让面试官觉得你只看了 2024 的博客。

上线门禁写清楚：哪些 action 只读、哪些要人工、记忆里禁止出现的字段、trace 保留多久。换 Nova 档位时这套契约不动，见 `amazon-nova`。延迟按整段编排报 p99，不要只报第一句模型 token。

## 追问

- **Lambda 和 return control 怎么选？** 无副作用或已幂等的只读，Lambda 快。写库、付款、需要应用事务的，return control，让已有服务做一次完整提交。
- **记忆和 session 属性差在哪？** Session 是这一轮的短状态；memory 是跨会话摘要。摘要不是原文日志，不能当审计源。审计看 CloudWatch / 你自己的事件表。
- **提示注入怎么办？** 工具结果当数据；不可逆动作不只靠 prompt；KB 块不要和系统策略糊成一段。Guardrails 是一层，不是全部。
- **为什么还要自建？** 托管省编排，不省责任。Bar Raiser 问的是失败模式所有权，不是你会不会点控制台。
