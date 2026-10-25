---
id: jd-skills-essence
section: agent
order: 190
level: A
title: 京东后端一面：Skills 的本质是什么？和 MCP 差在哪一层？
quick: "Skill 本质是按需加载的任务说明书，写清触发条件、步骤、允许的工具子集、权限边界和验收标准，管「这件事按什么流程做对」。MCP 是协议层，负责工具的发现、连接和调用格式。没有 Skill，模型对着一堆工具临场拼流程；没有 MCP，每个工具都要手写连接。"
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

Skill 的本质是一份按需展开的任务说明书，写清触发条件、步骤、允许用的工具、权限边界和验收标准，它管的是「这件事按什么流程做对」。MCP 在它下面一层，是协议，负责发现外部能力、建立连接、约定调用格式。没有 Skill，模型会对着一堆工具临时乱拼；没有 MCP，每个工具都要手写连接。把 Skill 答成 Java `@Tool` 注解，或者把 MCP 说成「就是 Function Calling」，都把层次弄混了。

拿零售的退货举例最清楚。MCP server 只暴露接口本身，比如 `query_order`、`create_refund`。`refund-unreceived` 这个 Skill 写明先调订单查询、再判断签收状态、允许用哪些售后接口、禁止直接改库存、失败了回到哪一步。Host 只把当前 Skill 允许的工具子集放进上下文，模型看不见全量接口。业务知识变了，改 Skill 文档的版本就行，连接协议不用动。

再细说一下 MCP（Model Context Protocol）。它让 Host 发现并调用外部能力，定义 tools / resources / prompts 的清单、schema、调用和返回格式，但不规定退货要先查订单再申请、失败了怎么降级。Function calling 更下一层，只描述模型怎么输出结构化调用。Skill 是编排知识（procedural package），算不上又一个 RPC；后端一面要是把 Skill 理解成「再包一层 HTTP」，就会和 MCP 说成同一层。Skill 的正文不必全部放进 system prompt，可以通过检索或路由按需加载，减少 token 用量。几个概念的五者对照见 `agent-skill-diff`，协议细节见 `agent-mcp`。

写 Skill 要带权限和验收，否则它只是一段更长的 prompt。允许的工具必须是子集，「本 Skill 可调任意 MCP」是不行的；验收要可检查，比如状态回写了哪几个字段、用户有没有看到单号。治理上 Skill 像规则包，版本、审批、回滚见 `ali-skill-vs-rules-governance`；按需展开、不一次灌全，见 `agent-skill-progressive`。

零售二面还会把 Skill 和长期记忆、超长 Prompt 连着问。记忆存状态，比如用户要上门取件、这单已申请；Skill 存做法；MCP 负责连接接口。SOP 别写进记忆库，用户偏好也别写进 Skill。Prompt 过长时，先加载当前 Skill 的短目录，正文按步骤展开，工具的大输出放到外面，见 `jd-long-memory`。评测 Skill 看任务成功、越权调用、有没有按步骤走，文档写得像不像无所谓，见 `agent-skill-eval`。

## 追问

**没有 Skill，只用 MCP 行不行？**
能调工具，但退货、价保这类复杂 SOP 要靠模型临场拼，越权和漏步骤都会变多。

**Skill 和 Workflow 是什么关系？**
Skill 是「这类任务该怎么做」的知识，Workflow 是预定义的控制图。约束强的链路可以把 Skill 编译成图，见 `meituan-workflow-vs-agent`。

**Skill 要不要微调进模型？**
易变的流程放文档里按需加载；只有稳定、高频、格式要求很死的调用，才值得做监督微调（SFT）。

**遇到恶意的 Skill 或工具描述怎么办？**
Host 要独立做权限和 schema 校验，description 不能当可信指令，见 `agent-skill-security`、`agent-prompt-injection`。
