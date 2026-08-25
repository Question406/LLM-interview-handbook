---
id: pdd-openclaw-spec-driven
section: agent
order: 185
level: A
title: 拼多多：OpenClaw 的记忆是什么？Spec-driven code agent 又在解决什么？
quick: >-
  OpenClaw 一类框架把记忆做成插件化、可检索的状态，别做成无限聊天记录。Spec-driven
  先写可验收规格再改代码，减少「先生成再猜测试」。两者都是 harness 设计，不是模型型号。
tags:
  - PDD
  - OpenClaw
  - Spec-driven
  - Memory
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 拼多多日常实习 大模型算法一面分享
    url: https://www.nowcoder.com/feed/main/detail/ba50ad3b3777443da540fcd9cfaf7377
    type: candidate-first-hand
  - title: OpenClaw Memory
    url: https://docs.openclaw.ai/concepts/memory/
    type: primary
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“玩过 Openclaw 吗？了解其的记忆机制吗？”**；**“了解过 spec-drivening 的 code agent 吗？”**

这块容易直接答成把记忆当成无限 append 的聊天记录，把 spec-driven 当成「先让模型写一段需求再写代码」。两者问的都是 harness：状态存在哪、何时写入、用什么当 verifier。没亲手翻过源码就不要编命令和内部文件名；讲清分层和验收闭环即可。规格侧对照 `byte-spec-sdd-openspec`。

## OpenClaw 一类记忆：文件化、分层、可检索

官方记忆模型把状态落成工作区里的 Markdown，别藏在向量库里当黑盒。长期事实进精炼层（如 `MEMORY.md`，会话开始加载），当日观察进 daily notes，需要时用 `memory_search` / `memory_get` 召回，别每轮整库注入。插件化的关键是：记忆变成带 schema 的存储，写入要过滤、过期和权限；未信任内容不能直接晋升长期层。面试可对应到通用三分法：工作记忆（当前任务槽位）、情景记忆（近期轨迹摘要）、长期记忆（跨会话检索）。要讲写入过滤，否则会记住过期地址，和 `pdd-compress-first-70` 的不可压缩状态是同一问题。没把源码背下来没关系，但要说清：模型只记得写进磁盘的东西，没有隐藏会话灵魂。

## Spec-driven：先有可验收规格，再改实现

Spec-driven code agent 先产出接口 / 测试 / 验收标准，再让模型改实现，用测试当 verifier。它解决的是「生成代码不可验证」。没有规格时，code agent 只能靠 diff 观感，失败了也不知道该重试哪一条断言。Harness 负责按规格执行、回放和失败重试；Spec 解决「对错可判定」，Harness 解决「判定之后谁执行」，见 `byte-spec-sdd-openspec`。SDD / Spec-kit / OpenSpec 都是把规格落成仓库约定，细节以你用过的为准，不要背营销名。

## 两者都是 harness，换模型替代不了

记忆决定「上下文从哪来、什么能留下」；规格决定「什么叫做对了」。电商 Agent 把地址写成可校验槽位，code agent 把接口写成测试，是同一类工程。评测看约束保持、测试通过和错误记忆晋升次数，别看「记了多少字」。诚实边界：用过哪一层 API 就说到哪一层，没跑过 OpenClaw 就说「同类物是文件化记忆 + 检索工具 + 写入门禁」。两问连在一起，是在看你会不会把框架当黑话：记忆是状态设计，spec-driven 是验收设计，都不是换一个更大的模型就能代替的 harness。

## 追问

- **记忆写入谁说了算？** 不能只靠模型自觉。要有过滤、过期、权限，未信任内容不得进长期层。
- **没有测试的 spec 算不算 spec-driven？** 不算。没有可自动判定的验收，仍然是观感驱动。
- **和 RAG 记忆有何区别？** RAG 检索外部文档；这类记忆是 Agent 自己的状态，要防污染和过期，见 `pdd-context-overflow`。
- **没玩过 OpenClaw 怎么答？** 承认范围，讲分层记忆和 spec-first 的通用设计，不要编源码细节。
