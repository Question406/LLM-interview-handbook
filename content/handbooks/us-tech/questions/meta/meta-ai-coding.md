---
id: meta-ai-coding
section: meta
order: 2
level: A
title: Meta：AI-enabled coding 轮怎么考？和普通 LeetCode 差在哪？
quick: >-
  这轮主要看你能否在约 60 分钟的多文件仓库任务里拆问题、审查 AI 的 diff 并跑测试。已有来源记录从 2025 年 10 月进入 onsite，AI
  可选；自己能解释 algorithm、edge cases 和纠错过程，比把代码全部交给助手更关键。
tags:
  - Meta
  - Coding
  - AI-assisted
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Meta's AI-Enabled Coding Interview — How to Prepare
    url: 'https://www.hellointerview.com/blog/meta-ai-enabled-coding'
    type: secondary
  - title: Inside Meta's New AI-Enabled Coding Round
    url: 'https://dglearning.substack.com/p/inside-metas-new-ai-enabled-coding'
    type: secondary
---

## 真题记录

- 公司：Meta
- 岗位：SWE / MLE / EM 的 onsite；E6 及以下常见「一轮传统 coding + 一轮 AI-enabled」
- 来源：Hello Interview 对内部试点说明和多位候选人的整理；2025-10 起进入 onsite，2026 已是默认形态之一
- 形态：CoderPad 三栏，约 60 分钟，一个加长的多文件题，分阶段推进（修 bug → 实现核心 → 优化）

这轮不是「LeetCode 允许开 ChatGPT」。仓库已经在那儿，测试能跑，模型菜单可能有 GPT / Claude / Llama / Gemini。评委看你怎么指挥和验收，不看你能不能写出花哨 prompt。

## 怎样完成这一轮

我会先把任务拆成能独立验证的小步，再决定哪些交给 AI。Hello Interview 转述的评分关注问题拆解、写与读代码、验证三个方面：先读文件树和失败测试，讲清不变式，再逐步实现；生成的脚手架可以采用，但 algorithm、edge cases、complexity 必须自己解释，不能只复制运行。

前 5 分钟先熟悉面试官介绍的环境，包括如何切模型、跑测试，然后打开失败测试，用一句话复述 spec。样板、重命名、明显的 getter 可以交给模型，带算法不变量的核心函数自己写或逐行审。模型可能比平时慢、弱，还会编 API，出现错误复杂度、共享状态或并发遗漏时，应直接说明原因并纠正。

来源转述的两层动机是贴近 Meta 工程师的实际工作，以及降低偷偷使用模型作弊的收益。AI 官方可选，不用模型但自己完成并通过测试，也可以过；始终让模型写、只点 Run，则难以展示沟通与判断。

另一轮传统 Meta coding 仍常是不能用 AI 的算法题。GenAI 的 ML 设计和研究答辩也不属于这一轮，时间应用在题目实现和验证上。

## 追问

**会按 prompt engineering 打分吗？**
来源没有把它列为评分项，重点是拆任务、审代码与跑通测试。

**模型太慢怎么办？**
选稳定的模型，卡住就自己写，避免空等。候选人报告中，GPT-5 一类有时比 Claude 慢，这是报告里的环境体验。

**怎么练习？**
Recruiter 通常会提供练习链接，没有就主动索取；也可以在本地用多文件仓库和任意助手做 60 分钟限时模拟。
