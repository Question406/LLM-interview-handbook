---
id: xiaohongshu-mcp-skill-token-efficiency
section: agent
order: 104
level: S
title: 小红书大模型后训练：MCP、Skill 有何区别，Skill 为什么能省 Token？
quick: >-
  MCP 是 host / client / server 之间连接工具、资源与提示的协议，不管 planning、memory 和 retry；Skill
  把一类任务的操作步骤、applicability limits 和 acceptance criteria 打包，供系统检索并管理版本。省 token
  来自渐进展开：全局只放短 metadata，路由到相关 Skill 后再按步骤加载说明和资源，MCP 协议本身不会压缩上下文。
tags:
  - Xiaohongshu
  - MCP
  - Skill
  - Context Engineering
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 小红书 大模型后训练一面（候选人原帖）
    url: 'https://www.nowcoder.com/discuss/872533899736334336'
    type: candidate-first-hand
  - title: Model Context Protocol
    url: 'https://modelcontextprotocol.io/'
    type: primary
  - title: Anthropic Agent Skills
    url: >-
      https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
    type: primary
---
## 真题记录

- 公司：小红书
- 团队 / 岗位：NLP / 多模态 / 大模型实习生；社区生态治理 Agent 开发方向
- 届别 / 流程：实习；一面
- 面试时间：2026-04-08 19:00
- 来源类型与可信度：牛客候选人原帖，A（公司、时间、岗位、轮次与业务方向明确）
- 原始措辞：**“MCP, SKILL 的区别，SKILL 为什么能省 Token？”**

MCP 和 Skill 管的是两层：MCP 解决应用怎样用标准方式发现、读取和调用外部 tools / resources，不规定模型怎样完成一类任务；Skill 把 workflow、applicability limits、examples、检验规则和少量资源封装成可检索、可版本化的操作知识。Skill 省 token，靠的是渐进展开，平时只放一小段描述，用到时才加载正文，协议本身不压缩上下文。说「MCP 比较省 token」或者「Skill 就是另一种 function calling」，都把两层混在一起了。

举个例子，若 1000 个 Skill 每个数千 token 全部放进 system prompt，上下文会被淹没；把所有 SOP 写成超长的 tool description 塞进 MCP，也一样不省 token，还更容易让模型选错工具。做成 Skill 以后，全局只保留每个 Skill 的 name、description 和触发条件；来了一条任务，先路由到少数几个相关的 Skill，再按步骤加载说明、模板或资源。

MCP 是 host / client / server 之间的能力与上下文协议，工具、资源、提示都可以按标准发现和调用，它不负责 planning、memory、retry。Skill 是某类任务的 procedural package，写清何时触发、输入输出、不适用场景和验收规则。执行时，Skill 可能通过 MCP 调具体能力，也可能走内部 API。社区治理里，审核标准更适合做成 Skill，规范更新时改版本，不用改死代码，见 `xiaohongshu-agent-business-eval`。协议层可以对照 `agent-mcp`。

渐进展开（progressive disclosure）分三层：第一层 metadata 必须短，但要能区分能力；第二层正文给 procedure；第三层脚本和参考资料只在具体 step 需要时加载，见 `agent-skill-progressive`。如果每轮仍然全文展开，Skill 只是多了一层包装。路由失败就等于这个 Skill 不存在，所以 description 要写清 applicability 和 when-not-to-use。

评测别只报省了多少字，要看 task success、路由 recall、展开的 token、误路由和 latency。治理场景还要看政策版本有没有加载对、有没有把无关类目的 SOP 展开。Skill 版本必须进调用 manifest，才能和模板回滚对齐，见 `pdd-prompt-template-versioning-rollback`。安全上，Skill 正文和 MCP resource 都是外部 trust boundary，描述里可能带注入，见 `agent-skill-security`。

## 追问

**MCP 本身省 token 吗？**
不省。省的是按需加载 Skill 和资源，协议只负责连接。

**Skill 和工具 schema 重复了怎么办？**
schema 描述调用面，Skill 描述何时用、怎么验收。别写两份互相矛盾的长文。

**metadata 太多怎么办？**
再做命名空间或一个小路由器，progressive disclosure 可以递归，见 `agent-skill-progressive`。

**每轮全文展开还能叫 Skill 吗？**
只是包装层。没有按需加载，就没有 token 收益。
