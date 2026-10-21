---
id: dt-tool-parallel
section: posttrain-data
order: 10
level: A
title: 工具数据要不要造并行调用？串行轨迹会教出什么坏习惯？
quick: "要造，但按数据依赖决定：天气、日历这类独立读取放在同一轮并行，先查 id 再写入必须串行。只有串行 ReAct 轨迹，模型会把能并行的也排成多轮，延迟和轮次都会涨。环境要真的并跑；并行里部分失败时保留成功结果、只恢复失败项；写操作默认不并行，工具返回不计生成损失。"
companies:
  - apple
tags:
  - Apple
  - Tool Use
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Berkeley Function Calling Leaderboard
    url: https://gorilla.cs.berkeley.edu/leaderboard
    type: primary
  - title: ToolLLM
    url: https://arxiv.org/abs/2307.16789
    type: primary
---

要造，但按调用之间的数据依赖来定。独立的读取，比如同时查天气和日历，可以放在同一轮并行；下一步需要上一步的返回值时，比如先查 id 再写入，必须串行。模型输出一个 JSON 数组，并不能证明这些调用真的可以并行。

## 只有串行轨迹会出什么问题

如果数据全是 ReAct 式的「想 → 调 → 看 → 再调」，学生会把本可并行的调用也串起来，延迟和轮次都会涨。合成时尤其容易这样，因为教师的推理链（CoT）习惯按线性步骤写。对延迟敏感的场景，两次独立读取排成两轮就是白白多一轮。公开评测里 BFCL 也有专门的并行 / 多工具切片。

## 怎么标依赖

对每个用户请求先画依赖图，找出哪些调用的输入不依赖其他调用的输出。这些独立调用合并成一轮并行，也就是一个 assistant 消息里放多个工具调用；有依赖的放到下一轮。

合成数据可以用规则做后处理，把 schema 和任务上没有数据依赖的调用合并到同一轮。然后人工抽查，看合并时有没有把「先查再改」错误地并行了，那样改的会是旧快照。

## 执行和 mask

并行调用要在环境里真的并发执行。如果框架其实还是串行跑，延迟数据就和实际部署对不上。并行调用返回的观测结果（observation）顺序要固定，比如按名字排序，否则监督微调（SFT）会去背顺序。所有工具返回仍用 mask 排除，不计入交叉熵损失（CE）。

## 部分失败和写操作

并行里一个失败、一个成功时，数据要示范：成功的结果留下，失败的重试或降级。既不要整轮作废，也不要假装全部成功，见 `dt-tool-error-recover`。

写操作默认不并行，见 `dt-tool-write-confirm`。如果两个写入抢同一条日历记录，环境里要有冲突处理的示范。

## 追问

- **小模型也要并行吗？** 要，能并就并。小模型更需要短轨迹，合并调用正好能减少轮次。
- **BFCL 的并行题能拿来训吗？** 当格式示范之前，先确认它不在门禁里。在自己的 schema 上造同构的依赖图更稳。
