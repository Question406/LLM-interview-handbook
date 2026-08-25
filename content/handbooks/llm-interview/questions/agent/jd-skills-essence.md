---
id: jd-skills-essence
section: agent
order: 190
level: A
title: 京东后端一面：Skills 的本质是什么？和 MCP 差在哪一层？
quick: >-
  Skill 是可按需展开的任务说明书（触发条件、步骤、允许工具、验收），管的是编排知识，不是又一个
  RPC。MCP 管连接与调用格式；Skill 管「这件事按什么流程做对」。没有 Skill 时模型会临时乱拼工具。
tags:
  - JD
  - Skills
  - MCP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 京东后端-一面
    url: https://www.nowcoder.com/feed/main/detail/ad9b86d7b29b4b5583840d0169458b0a
    type: candidate-first-hand
  - title: 京东零售平台产品与研发中心二面
    url: https://www.nowcoder.com/feed/main/detail/6a94272eee68460d9e8f90c72ddb8dab
    type: candidate-first-hand
---

## 真题记录

- 公司：京东
- 岗位：后端一面；零售平台产品与研发中心二面也问 MCP / Skill
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“skills的本质是什么”**；**“MCP和Skill是什么，有什么区别”**

这块容易直接答成 Java `@Tool` 注解，或把 MCP 说成「就是 Function Calling」。京东后端和零售岗连问这两词，要的是分层：一层协议负责发现和调用，一层程序负责「这件事按什么流程做对」。没有 Skill 时模型会对着一堆工具临时乱拼；没有 MCP 时每个工具都要手写连接。五者对照见 `agent-skill-diff`，协议细节见 `agent-mcp`。

## 一层协议，一层程序

MCP（Model Context Protocol）让 Host 发现并调用外部能力：tools / resources / prompts 的清单、schema、调用与返回格式。它不规定退货要先查订单再申请、失败如何降级。Function calling 只描述模型如何输出结构化调用，更下一层。

Skill 是可按需展开的任务说明书：触发条件、步骤、允许工具、权限边界、验收标准。正文不必塞进 system prompt，按检索或路由加载以省 token。说白了是编排知识（procedural package），不是又一个 RPC。零售例子：`refund-unreceived` Skill 写明先调订单查询、再判断签收状态、允许的售后接口、禁止直接改库存；MCP server 只暴露这些接口本身。

写 Skill 要带权限和验收，否则只是更长的 prompt。允许工具必须是子集，不能「本 Skill 可调任意 MCP」。验收要可检查：状态回写了哪几个字段、用户是否看到单号。治理上 Skill 像规则包，版本、审批、回滚见 `ali-skill-vs-rules-governance`；按需展开而不是一次灌全见 `agent-skill-progressive`。

## 和记忆、超长 Prompt 的边界

零售二面会把 Skill 和长期记忆、超长 Prompt 连问。记忆存状态（用户要上门取件、这单已申请），Skill 存做法，MCP 存货（接口）。不要把 SOP 写进记忆库，也不要把用户偏好写进 Skill。Prompt 过长时先加载当前 Skill 的短目录，正文按步骤展开，工具大输出外置，见 `jd-long-memory`。评测 Skill 看任务成功、越权调用和是否按步骤走，别看文档写得像不像，见 `agent-skill-eval`。后端一面若把 Skill 理解成「再包一层 HTTP」，会和 MCP 说成同一层。可以当场用退货举例：MCP server 列出 `query_order` / `create_refund`；Skill 规定先查询、看签收、再决定能否申请、失败回哪一步。Host 只把当前 Skill 允许的工具子集放进上下文，模型无法看见全量接口。知识改变时改文档版本，不必改连接协议。

## 追问

- **没有 Skill 只用 MCP 行不行？** 能调工具，但复杂 SOP（退货、价保）会靠模型临场拼，越权和漏步骤会涨。
- **Skill 和 Workflow 什么关系？** Skill 是「这类任务应如何做」的知识；Workflow 是预定义控制图。强约束链路可以把 Skill 编译成图，见 `meituan-workflow-vs-agent`。
- **Skill 要不要微调进模型？** 易变流程放文档按需加载；只有稳定、高频、格式要求死的调用才值得 SFT。
- **恶意 Skill / 工具描述怎么办？** Host 必须独立做权限与 schema，不能把 description 当可信指令，见 `agent-skill-security`、`agent-prompt-injection`。
