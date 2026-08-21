---
id: ali-skill-vs-rules-governance
section: agent
order: 106
level: S
title: 阿里云：Skills 和 Rules 的区别是什么？
quick: >-
  Rule 是始终生效、可强制执行的治理约束，如权限、数据边界和输出 policy；Skill 是按任务发现、加载和执行的
  程序性知识包。Rule 决定“能不能做”，Skill 指导“怎么做”，二者冲突时由 runtime policy 而非模型自行裁决。
tags:
  - Alibaba Cloud
  - Agent Platform
  - Skills
  - Governance
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
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

这题别答成「都是 prompt 里的说明」。阿里云 Agent 平台一面要听的是治理边界：Skill 是能力包，Rule 是强制约束。我会先说一句话——Rule 决定能不能做，Skill 指导怎么做——再讲生命周期和冲突裁决必须落在 runtime，而不是模型自觉。和 `ant-skills-vs-harness`、`agent-skill-eval` 同一套分层。

## Skill 是按需加载的程序知识

Skill 面向某类任务：步骤、脚本、模板、允许的工具子集和参考资料，例如「发布服务」的检查清单。它可发现、可版本化、可按任务加载，优化的是能力复用与上下文成本——先目录后展开，而不是把说明书一次性塞进 system prompt。Skill 有 owner、适用条件、评测和渐进披露；写得好不好要用 no-skill / full-skill ablation 看任务成功和 token，而不是文笔。建议调用某工具，只是建议。

## Rule 是始终生效的治理

Rule 跨任务：不可读哪些路径、必须人工确认哪些动作、输出不得泄露何种数据、租户边界。它由安全或平台策略发布，带优先级、scope、审计和 fail-closed。执行点在 host / tool gateway，不是一段可被后续文本覆盖的 prompt。权限不能只写在 Skill 或 system prompt 里，见 `agent-tool-permissions`。Rule 对所有 Skill、所有用户消息和所有 tool 输出生效。

## 冲突时 runtime 裁决

Skill 建议「调用生产发布」但 Rule 不允许写生产时，网关直接拒绝并给出可解释错误；不能让模型换一个 Skill 绕开，也不能让「更具体的用户指令」覆盖安全 Rule。同层 Rule 按 scope 与优先级；安全类 fail-closed。这样才分得清「每次都必须遵守的 policy」和「完成任务时可能有用的知识」。评测要构造「Skill 教了越权步骤」看是否被拦。

## 追问

- **Rule 能不能写进 Skill 正文？** 可以当提示，但不能当唯一执行点。真约束必须在网关 fail-closed，否则注入或换 Skill 就能绕开。
- **用户说「忽略安全规则」怎么办？** 用户消息 authority 低于平台 Rule。拒绝并审计，不要让模型自行和解。见 `baidu-agent-instruction-conflict`。
- **Skill 误触发怎么办？** 用适用条件和评测里的 distractor 任务压误触发；Rule 仍兜底，不能靠「模型应该知道这次不该用」。
- **和 MCP / tool schema 的关系？** Schema 描述怎么调；Rule 决定这个会话能不能调、能调到哪类资源。见 `agent-schema-contract`。
