---
id: xiaohongshu-mcp-skill-token-efficiency
section: agent
order: 104
level: S
title: 小红书大模型后训练：MCP、Skill 有何区别，Skill 为什么能省 Token？
quick: >-
  MCP 是 host / client / server 连接工具、资源与提示的协议；Skill 是某类任务的可发现、可版本化 procedural knowledge package。
  Token 节省来自把大量操作说明 / 资源按需检索和渐进展开，MCP 协议本身不会天然压缩上下文。
tags:
  - Xiaohongshu
  - MCP
  - Skill
  - Context Engineering
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 小红书 大模型后训练一面（候选人原帖）
    url: https://www.nowcoder.com/discuss/872533899736334336
    type: candidate-first-hand
  - title: Model Context Protocol
    url: https://modelcontextprotocol.io/
    type: primary
  - title: Anthropic Agent Skills
    url: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
    type: primary
---
## 真题记录

- 公司：小红书
- 团队 / 岗位：NLP / 多模态 / 大模型实习生；社区生态治理 Agent 开发方向
- 届别 / 流程：实习；一面
- 面试时间：2026-04-08 19:00
- 来源类型与可信度：牛客候选人原帖，A（公司、时间、岗位、轮次与业务方向明确）
- 原始措辞：**“MCP, SKILL的区别，SKILL为什么能省Token？”**

这块容易直接答成「MCP 比较省 token」或「Skill 就是另一种 function calling」。MCP 解决应用如何标准地发现、读取与调用外部 tools / resources，不规定模型怎样完成一类任务。Skill 把 workflow、边界、示例、检验规则与少量资源封装成可检索、可版本化的操作知识。Token 节省来自渐进展开，不是协议本身压缩上下文。协议层对照 `agent-mcp`，展开层对照 `agent-skill-progressive`。

## MCP 是连接，Skill 是操作知识

MCP 是 host / client / server 之间的能力与上下文协议：工具、资源、提示可以标准发现和调用。它不负责 planning、memory、retry。Skill 是某类任务的 procedural package：何时触发、输入输出、不适用场景、验收规则。执行时可能通过 MCP 调具体能力，也可能走内部 API。社区治理里，审核标准更适合做成 Skill：规范更新改版本，而不是改死代码，见 `xiaohongshu-agent-business-eval`。把所有 SOP 写成超长 tool description 塞进 MCP，既不省 token，也加重误选。

## 省 token 的条件是 progressive disclosure

全局只保留短 metadata（name / description / 触发条件），先路由到少数相关 Skill，再按步骤加载说明、模板或资源。若 1000 个 Skill 每个数千 token 全进 system prompt，上下文会被淹没。第一层 metadata 必须短但能区分能力；第二层正文给 procedure；第三层脚本和参考只在具体 step 需要时加载，见 `agent-skill-progressive`。如果每轮仍全文展开，Skill 只增加包装层。路由失败等于 Skill 不存在，所以 description 要写清边界和「不适用」。

## 要测什么，别只报省了多少字

看 task success、路由 recall、展开 token、误路由与 latency。治理场景还要看政策版本是否加载对、有没有把无关类目 SOP 展开。Skill 版本必须进调用 manifest，才能和模板回滚对齐，见 `pdd-prompt-template-versioning-rollback`。安全上，Skill 正文和 MCP resource 都是外部信任边界，描述可能带注入，见 `agent-skill-security`。

## 追问

- **MCP 本身省 token 吗？** 不省。省的是按需加载 Skill / 资源，协议只负责连接。
- **Skill 和 tool schema 重复怎么办？** schema 描述调用面，Skill 描述何时用、怎么验收；不要两份互相矛盾的长文。
- **metadata 太多怎么办？** 再做命名空间或小路由器，progressive disclosure 可以递归，见 `agent-skill-progressive`。
- **每轮全文展开还能叫 Skill 吗？** 包装层而已。没有按需加载就没有 token 收益。
