---
id: amazon-bedrock-agents
section: amazon
order: 12
level: A
title: Amazon：Bedrock Agents 的工具、记忆、护栏，和自建 harness 怎么选？
quick: >-
  Bedrock Agents 可以托管工具选择、检索和会话编排，权限、确认、预算和沙箱仍由应用负责。工具少且流程稳定时用托管；涉及事务、补偿或精细重试时自建
  harness，也可以只把写操作交回自己的服务。
tags:
  - Amazon
  - Bedrock
  - Agents
  - Tools
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Automate tasks in your application using AI agents
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html'
    type: primary
  - title: How Amazon Bedrock Agents work
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html'
    type: primary
  - title: Retain conversational context across sessions using memory
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/agents-memory.html'
    type: primary
  - title: Detect and filter harmful content with Amazon Bedrock Guardrails
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html'
    type: primary
---

我会按需要多少编排控制权来选。工具少、流程稳定时，托管 Agents 能省掉一部分循环代码；退款、改地址这类有副作用的动作，可以 return control 交回应用服务确认和提交。Classic Agents 与 AgentCore 的产品状态也要区分，不能只依据 2024 年的博客：原文所引文档写的是 Classic 对新客户关闭，新能力看 AgentCore。

## 托管流程和应用责任怎么分

Classic Agents 编排 FM、数据源和会话。Action Group 用 OpenAPI 或 function schema（函数参数的字段和类型定义）描述工具，可以接 Lambda，也可以 return control。一次 `InvokeAgent` 会理解用户、选 action 或 KB、填参执行、观察结果，再决定继续还是结束。预处理、编排、KB 和后处理提示模板都可以调整，trace 则展示各步 rationale。

应用还要自己实现下面这些 safeguards：

- **工具权限和副作用。** Schema 能描述参数，不能描述「退款超过限额要人工」。不可逆动作要确认框或 return control，让应用层拍板，不要让模型直接打生产 Lambda。
- **预算。** 调用步数、token 数、实际耗时和重试次数。托管循环会转，直到模型说结束或你超时。没有明确上限就会在工具抖动时空转。
- **沙箱。** Lambda 是你的运行时：VPC、IAM、密钥、出网。Agent 不管 kernel。工具 stdout / 网页 / PDF 都是不可信输入，进下一轮 prompt 前要截断、当数据不当指令。
- **记忆。** 文档：默认同 session；打开 memory 后，在 `endSession` 或 idle 超时后异步摘要，按 `memoryId` 存最多可到 365 天。摘要会丢细节、也会把不该长期记的 PII 写进去。用户级隔离是你传对 id；多用户共用一个 memoryId 就是串话。删记忆是产品功能，不是「模型会忘」。

Knowledge Base 提供检索增强生成（RAG），agent 决定何时检索；引用、过期条款处理和混合检索仍要单独设计，不能假设用了 KB 就一定有证据支持。

Guardrails 分别检查输入和输出，前者拦越狱和拒答主题，后者拦 hallucination / PII。Contextual grounding 只对输出有意义，流式输出还要处理检查时机与首 token 延迟的冲突。

## 何时用托管，何时自建

根据这些要求选择编排方式：

- **托管 Agents / AgentCore。** 工具少而稳、API 已有 OpenAPI、要快速上内部助手、审计用 trace 就够。换模型时策略仍在 Guardrails 和应用 IAM。
- **自建 harness。** 要多步事务、补偿、人工确认、精细重试、和内部工作流引擎对接、或必须在工具之间做确定性状态机。模型只出结构化调用，循环在你的代码里。
- **混合。** 只读查询走托管；下单、改地址、退款 return control 回自己的服务。这往往是生产默认。

评测看工单是否解决、工具选择和权限错误、步数分布、记忆串话，以及 Guardrail 漏拦和误拦。离线用带金标工具轨迹的 case，线上看升级工单和事故，再把失败轨迹写回回归集。

OpenAPI 只描述接口，不能替代权限检查；记忆也要限制长期保留的字段。Automated Reasoning 或业务规则这类政策引擎仍应在工具层执行。

release criteria 写清楚：哪些 action 只读、哪些要人工、记忆里禁止出现的字段、trace 保留多久。换 Nova 档位时这套契约不动，见 `amazon-nova`。延迟按整段编排报 p99，才能反映用户等到任务完成的时间。

相关：`amazon-guardrails`、`design-agent-harness`、`amazon-bedrock-rag`、`amazon-kendra-hybrid`、`amazon-p99-stream`、`amazon-titan-eval`。

## 追问

**Lambda 和 return control 怎么选？**
无副作用或已幂等的只读，Lambda 快。写库、付款、需要应用事务的，return control，让已有服务做一次完整提交。
**记忆和 session 属性差在哪？**
Session 是这一轮的短状态；memory 是跨会话摘要。摘要不是原文日志，不能当审计源。审计看 CloudWatch / 你自己的事件表。
**prompt injection 怎么办？**
工具结果当数据；不可逆动作不只靠 prompt；KB 块不要和系统策略糊成一段。Guardrails 是一层，不是全部。
**为什么还要自建？**
托管省编排，不省责任。Bar Raiser 问的是发生失败后由谁负责，不是你会不会点控制台。
