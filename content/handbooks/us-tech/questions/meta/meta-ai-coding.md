---
id: meta-ai-coding
section: meta
order: 2
level: A
title: Meta：AI-enabled coding 轮怎么考？和普通 LeetCode 差在哪？
quick: >-
  从 2025 年 10 月起，onsite 有一轮 60 分钟、多文件仓库，编辑器里带 LLM 助手。考的不是 prompt 竞赛，是你能不能拆任务、读懂
  AI 写出的 diff、跑测试、抓住幻觉。AI 是可选的，抄完却讲不清的会挂。
tags:
  - Meta
  - Coding
  - AI-assisted
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Meta's AI-Enabled Coding Interview — How to Prepare
    url: https://www.hellointerview.com/blog/meta-ai-enabled-coding
    type: secondary
  - title: Inside Meta's New AI-Enabled Coding Round
    url: https://dglearning.substack.com/p/inside-metas-new-ai-enabled-coding
    type: secondary
---

## 真题记录

- 公司：Meta
- 岗位：SWE / MLE / EM 的 onsite；E6 及以下常见「一轮传统 coding + 一轮 AI-enabled」
- 来源：Hello Interview 对内部试点说明和多位候选人的整理；2025-10 起进入 onsite，2026 已是默认形态之一
- 形态：CoderPad 三栏，约 60 分钟，一个加长的多文件题，分阶段推进（修 bug → 实现核心 → 优化）

这轮不是「LeetCode 允许开 ChatGPT」。仓库已经在那儿，测试能跑，模型菜单可能有 GPT / Claude / Llama / Gemini。评委看你怎么指挥和验收，不看你能不能写出花哨 prompt。

## 官方在看的三件事

Hello Interview 转述的能力模型大致是：

1. **拆问题。** 不要把整份题面贴进聊天。先读文件树和失败测试，说出不变式，再把工作切成可验证的小步。
2. **写代码、也读代码。** AI 给的脚手架可以留，算法和边界必须你过一遍。复制后讲不出复杂度或 invariant，和没写一样。
3. **验证。** 跑测试、补 case、看 AI 有没有漏掉的失败路径。模型在面试环境下经常变弱、变慢、会幻觉 API。

内部说明里写过两层动机：这更接近 Meta 工程师现在的工作方式；以及「既然允许用模型，偷偷用模型作弊就没那么值钱」。AI 官方是可选的，不用模型但自己把测试跑绿，完全可以过。反过来，全程让模型写、自己只点 Run，过不了沟通这一栏。

## 现场怎么打

前 5 分钟听面试官介绍环境：怎么切模型、怎么跑测试。然后自己打开失败测试，用一句话复述 spec。机械活（样板、改名字、写明显的 getter）可以丢给模型。带算法不变量的核心函数自己写或逐行审。

模型建议明显错时要说出来：错的复杂度、错的共享状态、漏掉的并发。这正是评委要的信号。

和传统 Meta coding 仍并存：另一轮往往是不能用 AI 的算法题。GenAI 岗的 ML 设计和研究答辩不在这轮里，不要把 60 分钟花在讲 Llama 论文。

## 追问

- **会不会考 prompt engineering？** 不是评分项。能把任务切对、把测试跑绿，prompt 土一点没关系。
- **模型很慢怎么办？** 候选人报告里 GPT-5 一类有时比 Claude 慢。选一个稳的，卡住就自己写，不要空等。
- **练习环境？** Recruiter 通常会发练习链接。没发就主动要。没有链接时，本地用多文件仓库 + 任意助手做 60 分钟限时模拟。
