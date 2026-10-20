---
id: p3a-anthropic-sd-q2-prompt-playground
section: anthropic
order: 625
level: A
title: "Anthropic：Prompt Playground：产品流程、schema 与共享"
quick: "Prompt playground 要定义好 prompt、版本、测试输入、运行结果和分享权限，并让用户始终清楚编辑和运行用的是哪一个版本。"
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
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · sd-q2-prompt-playground"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/sd-q2-prompt-playground
    type: secondary
---

## 题目

题面已经给出部署图，要求设计一个协作式的 prompt 试验产品，重点讨论用户流程、数据结构和 UX。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

先定义几个实体：prompt、版本、测试输入、运行结果和分享权限，并说清楚编辑时改的是哪个版本、运行时用的又是哪个版本。

并发编辑、失效的分享链接、敏感测试样例和失败重跑，在界面上都要有可见的状态。题目已经给了部署图，就按给定范围讨论产品和数据，不要整轮都在重复画架构图。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

已给出"客户端 → 服务端 → 数据库"的部署图，要求设计协作式的 prompt 试验产品。重点是用户流程、数据结构、分享和边界情况。

开始回答时复述这些范围，问面试官目标用户是个人开发者还是团队。

### 一套可展开的参考答案

**1. 用户主流程。** 依次是：

1. 创建项目。
2. 编辑 prompt。
3. 保存版本。
4. 在测试样例上运行。
5. 对比不同版本的结果。
6. 分享给同事。

界面同时展示草稿和已保存版本；运行只使用某个已保存版本，或者一份显式的快照。

**2. 数据模型和权限。** 实体包括 project、`prompt_version`、`dataset_case`、run、comparison 和 `share_permission`。编辑者能改内容；查看者只能看授权给他的版本和结果。机密样例单独控制访问。

**3. 走一遍一次对比。** 用户在 v3 的基础上改了系统提示，存成 v4。他选中项目里的 20 条 `dataset_case`，同时对 v3 和 v4 发起运行，界面为每个版本显示一列结果，正在跑的格子显示进度。全部完成后生成一条 comparison 记录，用户把它分享给同事；同事打开链接看到的是 v3、v4 这两个固定版本的结果，而不是作者此后的草稿。

**4. 失败、重复与恢复。**

- 两人同时保存时提示冲突，不用 last-write-wins 静默覆盖。
- 运行失败可以重试，原来的输出保留。
- 撤销分享立即生效；链接被转发不会自动扩大权限。

**5. 产品指标。** 衡量从创建项目到第一次成功运行的时间、用错版本的次数、分享导致的泄露，以及对比结果的可复现率。这道题的重点不是 API 吞吐。

### 面试追问与参考回答

**分享"最新版本"该怎样表达？** 默认分享固定版本。"跟随最新"要有明显的开关并记录审计，避免用户以为分享的是快照，结果后续加进去的敏感内容也被看到。

**测试样例里有客户数据怎么办？** 把这类样例标为机密，只有被单独授权的成员能看原文；分享 comparison 时，没有权限的人只看到模型输出和评分，看不到输入原文。
