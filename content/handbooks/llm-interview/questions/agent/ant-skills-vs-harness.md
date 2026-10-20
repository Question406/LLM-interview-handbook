---
id: ant-skills-vs-harness
section: agent
order: 181
level: A
title: 蚂蚁一面：Skills 怎么写？Spring AI 的调用更像 Claude Code 还是别的 Harness？
quick: "Skill 按需提供任务步骤、约束和可用工具；Tool Schema 则描述工具的参数。Harness 决定何时加载 Skill，以及如何隔离不可信输出。Spring AI 默认更接近注册工具后循环调用；Claude Code 还会按需读取资料并用 grep 搜索工作区，两者的运行方式不同。"
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

同一面先问怎么写 Skill，再对比 Spring AI 和 Claude Code。常见误区是：把 `@Tool` 注解当成 Skill，或把所有 harness 画等号。Skill vs Rule 见 `ali-skill-vs-rules-governance`；grep vs 检索增强生成（RAG） 见 `ant-grep-vs-rag`；Skill 评测见 `agent-skill-eval`。

## Skill 怎么写

写目标、前置条件、允许工具、检查清单、失败回退；正文短，细节文件按需读。节省 token 的方法是先读取目录，再按需展开具体内容，不是把说明书一次性塞进 system 输入提示（prompt）。Skill 是程序性知识，不是又一份 tool 字段和类型规范（schema）：schema 描述参数，Skill 描述何时用、先做什么、失败怎么停。触发条件要窄，避免相邻任务误加载。写 procedure，不要把评测答案写进文档。

## Harness 才决定怎么调用

Harness 负责何时加载 Skill、工具输出如何隔离、权限在哪执行。Claude Code 用工作区检索（grep）按需拉文件，工具面相对窄，上下文由探索构成，Skill 渐进披露。Spring AI 常见路径是预先暴露一组 `@Tool`，循环 function call，更像经典 tool-calling Agent。若项目里的「Skill」只是 Java 方法注解，应主动说：更接近 tool catalog，还不是 Claude 那种渐进披露。不要硬说「Spring AI 就是 Claude Code」。Harness 工程化还可对照 `byte-harness-engineering`。

## 对比时怎么落到一句

面试官要听的是你分得清三层：模型、Skill 文本、运行时 harness。同一模型换 harness，行为可以完全不同。Spring AI 也能做成渐进披露，把 Skill 当资源按需读、工具默认少暴露，但这需要项目自行配置，框架默认并不提供这套流程。默认 tool-calling 循环没有工作区搜索，就不要声称「和 Claude Code 一样」。

## 追问

- **Skill 和 tool 重复了怎么办？** Tool 是能力；Skill 是用法。冲突时 Rule / 权限网关说了算，Skill 不能授权新工具。
- **为什么 Claude Code 爱 grep？** 代码要精确符号和新鲜工作区，向量索引容易过期。见 `ant-grep-vs-rag`。
- **怎样证明 Skill 有用？** no-skill / metadata-only / full-skill ablation，看成功率和 token，并测误触发。见 `agent-skill-eval`。
- **Spring AI 怎样更接近 Claude？** 缩小默认工具面、Skill 按需读文件、用搜索而不是一次塞全量 schema；权限仍在网关。
