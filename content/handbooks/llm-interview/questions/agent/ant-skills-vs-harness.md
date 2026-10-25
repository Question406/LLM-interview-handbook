---
id: ant-skills-vs-harness
section: agent
order: 181
level: A
title: 蚂蚁一面：Skills 怎么写？Spring AI 的调用更像 Claude Code 还是别的 Harness？
quick: "Skill 按需提供任务步骤、约束和可用工具，Tool Schema 只描述参数；Harness 决定何时加载 Skill、怎么隔离不可信输出。Spring AI 默认更像注册工具后循环调用，Claude Code 还会按需读资料、用 grep 搜索工作区，两者运行方式不同。"
tags:
  - Ant Group
  - Skills
  - Harness
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 【面经】5月20日，蚂蚁智能体与大模型应用 一面
    url: https://www.nowcoder.com/discuss/888874988554448896
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：智能体与大模型应用
- 届别 / 流程：一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“项目的skills是怎么实现的？你是怎么写skills的？”**；**“Spring AI框架的skills调用更像Claude Code还是其他Harness agent？”**

Skill 是按需展开的任务说明，写什么时候用、先做什么、能用哪些工具、失败怎么停；Tool Schema 只描述参数。Harness 决定什么时候加载 Skill、工具输出怎么隔离、权限在哪执行。Spring AI 默认更接近「预先暴露一组 `@Tool`、循环 function call」的经典 tool-calling Agent；Claude Code 还会用 grep 按需读工作区、渐进披露 Skill，两者运行方式不同。所以别把 `@Tool` 注解当成 Skill，也别把所有 harness 画等号。

先说 Skill 怎么写。正文写目标、前置条件、允许的工具、检查清单和失败回退，尽量短，细节放在文件里按需读。省 token 的办法是先读目录、再按需展开具体内容，一次性把说明书塞进 system 输入提示（prompt）就省不下来。Skill 是程序性知识，和 tool 的字段和类型规范（schema）分工不同：schema 描述参数，Skill 描述何时用、先做什么、失败怎么停。触发条件要窄，免得相邻任务误加载；写的是 procedure，别把评测答案写进文档。Skill 和 Rule 的区别见 `ali-skill-vs-rules-governance`，Skill 怎么评测见 `agent-skill-eval`。

再说 Harness。举个例子，同样一个「修复失败测试」的 Skill，放在 Claude Code 里，Agent 先用工作区检索（grep）找到相关文件、按需拉取，Skill 也是渐进披露的，工具面比较窄，上下文是探索出来的；放在 Spring AI 的常见用法里，一组 `@Tool` 预先暴露给模型，然后循环调用。如果项目里的「Skill」只是 Java 方法上的注解，应该主动说明：它更接近 tool catalog，还算不上 Claude 那种渐进披露。别硬说「Spring AI 就是 Claude Code」。grep 和检索增强生成（RAG）的区别见 `ant-grep-vs-rag`。

所以对比时落到一句话，面试官想听的是你分得清三层：模型、Skill 文本、运行时 harness。同一个模型换一套 harness，行为可以完全不同。Spring AI 也能做成渐进披露，把 Skill 当资源按需读、默认少暴露工具，但这要项目自己配置，框架默认不提供这套流程。默认的 tool-calling 循环没有工作区搜索，就别声称「和 Claude Code 一样」。Harness 工程化可以对照 `byte-harness-engineering`。

## 追问

**Skill 和 tool 重复了怎么办？**
Tool 是能力，Skill 是用法。冲突时 Rule / 权限网关说了算，Skill 不能授权新工具。

**为什么 Claude Code 爱用 grep？**
代码要精确符号和新鲜的工作区，向量索引容易过期，见 `ant-grep-vs-rag`。

**怎样证明 Skill 有用？**
做 no-skill / metadata-only / full-skill 的 ablation，看成功率和 token，同时测误触发，见 `agent-skill-eval`。

**Spring AI 怎样更接近 Claude？**
缩小默认工具面，Skill 按需读文件，用搜索替代一次塞全量 schema；权限仍然放在网关。
