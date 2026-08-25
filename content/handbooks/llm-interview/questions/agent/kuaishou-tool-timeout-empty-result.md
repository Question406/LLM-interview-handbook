---
id: kuaishou-tool-timeout-empty-result
section: agent
order: 109
level: A
title: 快手：工具调用超时或空返回时，如何让 Agent 正确反馈用户？
quick: >-
  Tool 返回必须区分 timeout、空集、权限拒绝和未知错误，并带 request ID、可重试性与下一步建议；Agent 先依据
  契约决定重试、换查询、降级或澄清。面对用户要诚实说明未完成与已尝试内容，绝不能把空结果编造成事实。
tags:
  - Kuaishou
  - Agent
  - Tool Calling
  - Error Recovery
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手大模型应用开发算法岗三面面经（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/4ff132d0d0fb450398341f4ec9828def
    type: candidate-first-hand
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型应用开发算法岗
- 届别 / 流程：原帖未披露；三面
- 面试时间：原帖未披露；帖子发布于 2026-04-02
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“如果工具调用超时或返回空值，你如何设计 Prompt 让 Agent 反馈用户？”**

这块容易直接答成让 prompt 把任何空 observation 都解释成「没查到」，或超时后直接对用户说「不存在」。快手应用开发三面问的是契约 + 策略，不是多写一句安慰。空集、超时、权限拒绝、上游故障的政策完全不同；写操作超时后盲着重试可能重复提交。字节侧按错误码分流见 `byte-tool-fail-retry`。评估 Agent 时超时 case 必须进集，见 `kuaishou-agent-eval-dims`。

## 先把工具契约写清楚，再写 Prompt

工具应返回分类错误码、request ID、deadline、是否可重试、已执行范围、可安全展示的摘要。至少区分：`timeout`、`empty_result`、`permission_denied`、`invalid_query`、`upstream_failure`。Prompt 只负责依据这些字段选动作，不能从「空字符串」自行脑补业务结论。

策略：

- `timeout` / 限流：有限次指数退避；写操作先查最终状态，带幂等键；
- `empty_result`：可缩小或改写查询一次，仍空则如实说「该条件下无记录」，不要补参知识；
- `permission_denied`：澄清或转人工，不重试同一调用；
- `invalid_query`：修参数或问用户，见 `agent-ask-clarify`；
- `upstream_failure`：降级缓存或人工渠道，不把故障说成业务空。

schema 与错误码是合同，见 `agent-schema-contract`。model-readable 错误和 user-facing 文案必须分开：前者给策略，后者给用户。

## 对用户诚实，并能量化误报

面向用户应包含：已完成步骤、不能确认的部分、下一步选择。例如「查询在约定时限内未返回，尚不能断言没有记录；可重试或改为更小时间范围」。禁止把 timeout 说成「没有这条数据」，也禁止把 empty 说成「系统出了点问题请稍后再试」而不给已尝试条件。

埋点：失败类型、重试成功率、把超时误报成空集的比例、用户二次追问率。规划层失败只重跑子图，见 `kuaishou-modular-planning`。高 QPS 下三工具同时超时，要有预算和部分成功合并，别三条都编造成功。Prompt 是策略的说明书，不是唯一实现；运行时仍要用规则闸门拦住「空结果当事实」。三面若把问题收成「Prompt 怎么写」，仍先答错误码和字段，再给用户句式模板：已尝试范围、不能确认什么、可选下一步。模板按错误码分叉，别写一段万能道歉。这样评测可以断言「timeout 回复不得出现『不存在』」。和规划的衔接是：执行器把错误码写回 state，规划器决定重跑子图还是对人澄清，模型不负责发明业务结论。

## 追问

- **只改 Prompt 够不够？** 不够。没有错误码和可重试标记，模型只能猜。Prompt 是策略层，契约在工具层。
- **写操作超时怎么办？** 先按幂等键查询最终状态，确认未生效再重试；不要对着同一创建接口连打。
- **空结果能不能让模型「合理推测」？** 高风险字段不行。可以建议缩小条件，但不能把推测写成已查实。
- **如何评测这套反馈？** 注入超时 / 空 / 权限 case，看是否诚实、是否误报、是否重复提交；不要只看最终任务成功。
