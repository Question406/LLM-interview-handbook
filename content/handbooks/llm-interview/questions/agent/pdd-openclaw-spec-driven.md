---
id: pdd-openclaw-spec-driven
section: agent
order: 185
level: A
title: 拼多多：OpenClaw 的记忆是什么？Spec-driven code agent 又在解决什么？
quick: >-
  OpenClaw
  一类框架把记忆做成插件化、分层、可检索的状态，长期事实进精炼层、按需召回，写入要过滤、过期和权限，别做成无限追加的聊天记录。Spec-driven 的
  code agent 先写可验收的规格和测试，再改实现，用测试当 verifier，减少「先生成再猜测试」。两者都是 harness
  设计，换模型型号替代不了。
tags:
  - PDD
  - OpenClaw
  - Spec-driven
  - Memory
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 拼多多日常实习 大模型算法一面分享
    url: 'https://www.nowcoder.com/feed/main/detail/ba50ad3b3777443da540fcd9cfaf7377'
    type: candidate-first-hand
  - title: OpenClaw Memory
    url: 'https://docs.openclaw.ai/concepts/memory/'
    type: primary
---

## 真题记录

- 公司：拼多多
- 团队 / 岗位：大模型算法日常实习
- 届别 / 流程：一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“玩过 Openclaw 吗？了解其的记忆机制吗？”**；**“了解过 spec-drivening 的 code agent 吗？”**

这两问考的都是 harness：状态存在哪、什么时候写入、用什么当验证器（verifier）。记忆决定上下文从哪来、什么能留下；spec-driven 决定什么叫做对了。常见的误区是把记忆当成无限 append 的聊天记录，把 spec-driven 当成「先让模型写一段需求再写代码」。没亲手翻过源码，就别编命令和内部文件名，讲清分层和验收 feedback loop 就够了。

先说 OpenClaw 一类的记忆。官方记忆模型把状态落成工作区里的 Markdown，没有藏在向量库里当黑盒。长期事实进精炼层，比如 `MEMORY.md`，会话开始时加载；当天的观察进 daily notes；需要时用 `memory_search` / `memory_get` 召回，不会每轮整库注入。插件化的关键是记忆变成带字段和类型规范（schema）的存储，写入要过滤、过期和权限，未信任的内容不能直接晋升到长期层。不讲写入过滤，就会记住过期的地址，这和 `pdd-compress-first-70` 里的不可压缩状态是同一个问题。对到通用的三分法，就是工作记忆（当前任务槽位）、情景记忆（近期轨迹摘要）、长期记忆（跨会话检索）。源码没背下来没关系，但要说清：持久记忆来自已保存的数据，新会话不会自动拥有之前没保存的状态。

再说 spec-driven。它先产出接口、测试和验收标准，再让模型改实现，用测试当 verifier，解决的是「生成的代码没法验证」。比如让 code agent 给接口加分页，没有规格时只能看 diff 顺不顺眼，失败了也不知道该重试哪一条断言；先把分 page boundaries 和越界行为写成测试，跑一遍就知道对不对。Spec 解决「对错可判定」，Harness 解决「判定之后谁执行」，按规格执行、回放和失败重试，见 `byte-spec-sdd-openspec`。SDD、Spec-kit、OpenSpec 都是把规格落成仓库约定，细节以你用过的为准，营销名不用背。

两件事放在一起看：电商 Agent 把地址写成可校验的槽位，code agent 把接口写成测试，是同一类工程。评测看约束保持、测试通过和错误记忆被晋升的次数，「记了多少字」说明不了问题。已证实的事实与未知部分也要讲：用过哪一层 API 就说到哪一层，没跑过 OpenClaw，就说同类产品是「文件化记忆 + 检索工具 + 写入 acceptance checks」。面试官把两问连在一起，是在看你会不会把框架当黑话：记忆是状态设计，spec-driven 是验收设计，换更大的模型替代不了这层 harness。

## 追问

**记忆写入谁说了算？**
不能靠模型自觉。要有过滤、过期和权限，未信任的内容不得进长期层。

**没有测试的 spec 算不算 spec-driven？**
不算。没有能自动判定的验收，还是靠观感驱动。

**和检索增强生成（RAG）的记忆有什么区别？**
RAG 检索外部文档；这类记忆是 Agent 自己的状态，要防污染和过期，见 `pdd-context-overflow`。

**没玩过 OpenClaw 怎么答？**
承认范围，讲分层记忆和 spec-first 的通用设计，别编源码细节。
