---
id: kuaishou-tool-timeout-empty-result
section: agent
order: 109
level: A
title: 快手：工具调用超时或空返回时，如何让 Agent 正确反馈用户？
quick: >-
  先让工具返回能区分超时、空集、权限拒绝和上游故障的错误码，带上 request ID、能不能重试和下一步建议，Agent
  按错误码决定重试、改查询、降级还是问用户。对用户如实说哪些做了、哪些还没确认，超时不能说成「没有这条数据」。Prompt 只写策略，运行时还要有
  rule-based checks 拦住把空结果当事实。
tags:
  - Kuaishou
  - Agent
  - Tool Calling
  - Error Recovery
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 快手大模型应用开发算法岗三面面经（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/4ff132d0d0fb450398341f4ec9828def'
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型应用开发算法岗
- 届别 / 流程：原帖未披露；三面
- 面试时间：原帖未披露；帖子发布于 2026-04-02
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“如果工具调用超时或返回空值，你如何设计 Prompt 让 Agent 反馈用户？”**

我会先改工具契约，再写 Prompt。超时、空集、权限拒绝、上游故障该怎么处理完全不一样，工具只回一个空字符串，模型只能猜，猜错了就会对用户说「不存在」。所以先让工具把失败分清楚，Prompt 照着字段选动作，最后给用户一句诚实的话。多写一句安慰解决不了这个问题。

举个例子，用户问「我上个月的退款到账了吗」，查询接口超时了。如果 prompt 写的是「没结果就告诉用户没查到」，模型就会回「没有找到您的退款记录」，用户以为退款丢了。合适的回复是「查询在约定时限内未返回，尚不能断言没有记录；可重试或改为更小时间范围」。

工具这边，返回里要有分类错误码、request ID、deadline、是否可重试、已执行范围，以及一段可以安全展示的摘要。错误码至少分五类：`timeout`、`empty_result`、`permission_denied`、`invalid_query`、`upstream_failure`。schema 和错误码约定了工具怎样返回结果，见 `agent-schema-contract`；字节那边按错误码分流的做法见 `byte-tool-fail-retry`。

每类对应一套动作。`timeout` 和限流做有限次指数退避；如果是写操作，先按 idempotency key 查最终状态，盲着重试可能重复提交。`empty_result` 可以缩小或改写查询再试一次，还是空就如实说「该条件下无记录」，别拿模型参数里的知识补出业务结论。`permission_denied` 不重试同一个调用，去澄清或转人工。`invalid_query` 修参数或问用户，见 `agent-ask-clarify`。`upstream_failure` 降级到缓存或人工渠道，别把故障说成业务上没有数据。给模型看的错误信息和给用户看的文案要分开：前者用来选策略，后者用来向用户说明情况。

对用户的回复按错误码分叉成模板，每个模板讲三件事：已经试了什么、哪些还不能确认、用户可以怎么选。一段万能道歉没有用；把 empty 说成「系统出了点问题请稍后再试」、却不说试过哪些条件，同样不诚实。模板分开以后，评测就能直接断言「timeout 回复不得出现『不存在』」。面试官要是把题目收窄成「Prompt 怎么写」，我也会先讲错误码和字段，再给句式模板。

Prompt 只是策略的说明书，运行时还要用 rule-based checks 拦住「空结果当事实」。执行器把错误码写回 state，规划器决定重跑子图还是找用户澄清，业务结论不交给模型发明；规划层失败只重跑子图，见 `kuaishou-modular-planning`。高 QPS 下三个工具同时超时，要有预算，把部分成功的结果合并，别把三条都编成成功。线上埋点记失败类型、重试成功率、把超时误报成空集的比例和用户二次追问率。

## 追问

**只改 Prompt 够不够？**
不够。没有错误码和可重试标记，模型只能猜。Prompt 是策略层，契约要在工具层定下来。

**写操作超时怎么办？**
先按 idempotency key 查询最终状态，确认没生效再重试，别对着同一个创建接口连着打。

**空结果能不能让模型「合理推测」？**
高风险字段不行。可以建议用户缩小条件，但推测的内容不能写成已经查实。

**这套反馈怎么评测？**
往评测集里注入超时、空结果、权限拒绝的 case，看回复是否诚实、有没有误报、有没有重复提交，最终任务成功只是其中一项。评估 Agent 时超时 case 必须进集，见 `kuaishou-agent-eval-dims`。
