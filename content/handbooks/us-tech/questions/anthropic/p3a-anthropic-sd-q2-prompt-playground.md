---
id: p3a-anthropic-sd-q2-prompt-playground
section: anthropic
order: 625
level: A
title: Anthropic：Prompt Playground：产品流程、schema 与共享
quick: >-
  我会把每次运行绑定到保存的 prompt
  版本或明确快照，让编辑、对比和分享都能指向同一份内容。草稿、运行状态和权限也要在界面上说清楚，避免同事看到的结果跟自己运行的不一致。
companies:
  - anthropic
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · Anthropic · sd-q2-prompt-playground
    url: >-
      https://www.1point3acres.com/interview/problems/company/anthropic/sd-q2-prompt-playground
    type: secondary
---

## 题目

题面已经给出部署图，要求设计一个协作式的 prompt 试验产品，重点讨论用户流程、数据结构和 UX。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

先定义几个实体：prompt、版本、测试输入、运行结果和分享权限，并说清楚编辑时改的是哪个版本、运行时用的又是哪个版本。

并发编辑、失效的分享链接、敏感测试样例和失败重跑，在界面上都要有可见的状态。题目已经给了部署图，就按给定范围讨论产品和数据，不要整轮都在重复画架构图。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

已给出"客户端 → 服务端 → 数据库"的部署图，要求设计协作式的 prompt 试验产品。重点是用户流程、数据结构、分享和 edge cases。

开始回答时复述这些范围，问面试官目标用户是个人开发者还是团队。

我会让运行和分享都绑定到明确的版本，这样用户才知道自己在比较什么。草稿可以继续编辑，但一次运行只能使用已保存的版本，或者用户明确创建的快照。

比如用户在 v3 上改系统提示，保存为 v4，选中 20 条 `dataset_case` 同时跑这两个版本。界面按版本显示两列结果，没跑完的格子显示进度；完成后保存为 comparison。分享出去的链接固定指向 v3 和 v4 的结果，后续草稿不会跟着变。

完整流程就是创建项目、编辑 prompt、保存版本、运行样例、对比结果，再分享给同事。数据里对应 project、`prompt_version`、`dataset_case`、run、comparison 和 `share_permission`。界面同时展示草稿和保存版本；编辑者能改内容，查看者只能看到获准访问的版本和结果，机密样例另行授权。

两个人同时保存时要提示冲突，last-write-wins 会静默覆盖别人的工作。失败运行可以重试，旧输出留着。撤销分享要立即生效，链接被转发也不能扩大权限。失效链接、失败重跑和敏感样例都需要可见状态。

验证产品时，我会看从建项目到第一次成功运行花了多久、有多少次用错版本、分享有没有泄露，以及结果能否复现。部署图已经给定为客户端、服务端和数据库，讨论重点就放在这些流程和 data access rules 上。

### 面试追问与参考回答

**分享"最新版本"该怎样表达？**
默认分享固定版本。"跟随最新"要有明显的开关并记录审计，避免用户以为分享的是快照，结果后续加进去的敏感内容也被看到。

**测试样例里有客户数据怎么办？**
把这类样例标为机密，只有被单独授权的成员能看原文；分享 comparison 时，没有权限的人只看到模型输出和评分，看不到输入原文。
