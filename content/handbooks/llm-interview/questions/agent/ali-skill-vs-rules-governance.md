---
id: ali-skill-vs-rules-governance
section: agent
order: 106
level: S
title: 阿里云：Skills 和 Rules 的区别是什么？
quick: "Rule 是始终生效、可强制执行的治理约束，比如权限、数据边界和输出 policy；Skill 是按任务发现、加载和执行的程序性知识包。Rule 决定能不能做，Skill 指导怎么做；两者冲突时由 runtime 在网关裁决，安全类 Rule fail-closed。"
tags:
  - Alibaba Cloud
  - Agent Platform
  - Skills
  - Governance
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里云 AI agent平台研发工程师 一面凉经（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/476de2514a3c457c8be774623549f4b1?sourceSSR=post
    type: candidate-first-hand
---
## 真题记录

- 公司：阿里云
- 团队 / 岗位：AI Agent 平台研发工程师
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露；帖子发布于 2026-04-28
- 来源类型与可信度：牛客候选人原帖，B（公司、岗位、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“skills和rules的区别？”**

Rule 决定能不能做，Skill 指导怎么做。Skill 是按任务加载的能力包，Rule 是对所有任务都生效的强制约束，两者冲突时由 runtime 裁决，不靠模型自觉。把两者都说成「prompt 里的说明」，就没答到阿里云 Agent 平台一面想听的治理边界。这和 `ant-skills-vs-harness`、`agent-skill-eval` 是同一套分层，答完定义再讲生命周期和冲突裁决。

举个例子：某个 Skill 建议「调用生产发布」，而 Rule 不允许这个会话写生产。网关直接拒绝，并给出可解释的错误；模型换一个 Skill 也绕不开，「更具体的用户指令」也覆盖不了安全 Rule。

Skill 面向某类任务，里面有步骤、脚本、模板、允许的工具子集和参考资料，比如「发布服务」的检查清单。它可发现、可版本化、按任务加载，优化的是能力复用和上下文成本，所以要先给目录再展开，别把说明书一次性塞进 system 输入提示（prompt）。Skill 有 owner、适用条件、评测和渐进披露；评估时对比不用 Skill 和完整使用 Skill 时的任务成功率与 token 消耗，说明文字写得流畅不算数。Skill 里建议调用某个工具，也只是建议。

Rule 跨任务生效：哪些路径不能读，哪些动作必须人工确认，输出不能泄露哪类数据，租户边界在哪。它由安全或平台策略发布，带优先级、scope、审计和 fail-closed，执行点在 host 或 tool gateway，一段可以被后续文本覆盖的 prompt 当不了执行点。权限写在 Skill 或 system 输入提示里也不够，见 `agent-tool-permissions`。Rule 对所有 Skill、所有用户消息和所有 tool 输出都生效。

冲突裁决的规则是：同层 Rule 按 scope 和优先级排，安全类 fail-closed。这样才分得清「每次都必须遵守的 policy」和「完成任务时可能有用的知识」。评测时专门构造「Skill 教了越权步骤」的用例，看能不能被拦住。

## 追问

**Rule 能不能写进 Skill 正文？**
可以当提示，但不能当唯一的执行点。约束必须在网关 fail-closed，否则注入或者换一个 Skill 就能绕开。

**用户说「忽略安全规则」怎么办？**
用户消息的 authority 低于平台 Rule。拒绝并审计，别让模型自己去和解，见 `baidu-agent-instruction-conflict`。

**Skill 误触发怎么办？**
用适用条件和评测里的 distractor 任务压低误触发，Rule 仍然兜底，不能指望「模型应该知道这次不该用」。

**Rule 和 MCP / tool 字段和类型规范（schema）是什么关系？**
Schema 描述怎么调，Rule 决定这个会话能不能调、能调到哪类资源，见 `agent-schema-contract`。
