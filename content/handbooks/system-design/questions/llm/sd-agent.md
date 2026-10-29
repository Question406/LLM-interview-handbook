---
id: sd-agent
section: llm
order: 26
level: A
title: 生产 Agent：工具权限、状态机与预算
quick: 假设助手要查订单再修改地址。查询可以重试，修改地址则必须知道是否已经成功，还要确认用户有权操作。
companies: []
tags:
  - System Design
  - 设计练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Anthropic：Building effective agents
    url: 'https://www.anthropic.com/engineering/building-effective-agents'
    type: primary
  - title: Google SRE Book：Service Level Objectives
    url: 'https://sre.google/sre-book/service-level-objectives/'
    type: primary
---

## 题目描述

设计能处理客服请求的 Agent，支持读订单、查政策、生成退款草稿与交给人工。手册练习默认退款需要用户确认，预算最多8次工具调用，不允许跨租户读取。请输出任务状态机、工具接口、authorization rules、记忆与审计，说明工具成功但响应丢失、恶意检索文本、预算用尽和人工接手时的行为。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 回答思路

> **问题与场景：** 假设助手要查订单再修改地址。
>
> **做法与原因：** 我会让执行状态持久化：模型提出动作，程序校验参数与授权，调用工具，保存结果，再决定继续或结束。
>
> **检查与取舍：** 验证超时后恢复、重复提交与权限变化。

## 可以这样回答

假设助手要查订单再修改地址。查询可以重试，修改地址则必须知道是否已经成功，还要确认用户有权操作。

我会让执行状态持久化：模型提出动作，程序校验参数与授权，调用工具，保存结果，再决定继续或结束。每项任务还要有时间、tokens 和调用预算。

验证超时后恢复、重复提交与权限变化。成功标准包括正确结果和合法执行，不能只看最后一句“已经完成”。

## 技术备查

## 参考答案与设计讨论

模型提出动作，宿主校验权限、参数和预算后执行；副作用用稳定业务标识，任务状态可恢复且可取消。

### 先选可验证的最小工作流

用任务状态记录输入、证据、待确认动作、工具结果和最终状态。模型可以建议工具调用，真正的执行器要检查当前用户权限、参数 schema、动作风险和剩余预算。可用确定性步骤完成的环节，不必都交给开放式模型循环。

### 副作用与恢复

退款确认绑定具体订单、金额、币种和有效期，参数改变后重新确认。工具执行使用稳定业务 idempotency key，超时先查执行状态；仅记录“模型说退款成功”不能作为业务结果。恢复任务时从持久化状态判断，避免重复执行。

### 安全、成本和观测

检索内容、网页和工具输出都是不可信数据，不能覆盖宿主权限。工具凭据不交给模型；沙箱按任务隔离。预算应同时考虑次数、token、时间与费用，超限返回部分结果并转人工。轨迹记录要保护个人信息。

### 示例与关联

用户说“可以退这笔99元”，系统确认成功后才提交；工具超时不能再扣一次业务额度。扩展见[生产 tool calling](?book=us-tech&section=design&question=design-tool-prod)、[客服助手](?book=us-tech&section=design&question=design-chat-tools)、[Agent harness](?book=us-tech&section=design&question=design-agent-harness)、[预算](?book=us-tech&section=design&question=design-agent-budget)、[浏览器 Agent](?book=us-tech&section=design&question=design-browser-agent)和[语音 Agent](?book=us-tech&section=design&question=design-voice-agent)。

