---
id: dt-tool-parallel
section: posttrain-data
order: 10
level: A
title: 工具数据要不要造并行调用？串行轨迹会教出什么坏习惯？
quick: "按数据依赖决定并行：天气与日历等独立读取可放同一轮，先查 id 再写入必须串行。环境也要实际并跑。并行部分失败时，保留成功结果，只恢复失败项；写操作要额外检查冲突，工具返回不计生成损失。"
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

先根据调用之间的数据依赖标注。独立的读取可以在一轮并行执行；下一步需要前一步返回时，必须串行。输出 JSON 数组本身并不能证明调用真的可以并行。

不这么选的理由：数据若全是 ReAct「想 → 调 → 看 → 再调」，学生会把可并行的也串起来，延迟和轮次都爆。教师的推理链（CoT）常按线性步骤写，合成时容易把本可并行的调用也排成串行。BFCL 有并行 / 多工具切片。产品端侧更在意：两次独立读取不要排成两轮。

苹果：用户日志不进基础模型。并行示范在许可环境里造，观测结果（observation） 仍 mask。

## 怎么标依赖

对每个用户请求先画图：哪些调用的输入不依赖其他调用的输出。独立集合并成一轮并行（一个 assistant 消息里多个 工具调用）。有依赖的下一轮再发。

合成时要用规则后处理：把 schema 和任务中没有数据依赖的调用合并到同一轮。人抽查看并包有没有把「先查再改」错误并行（改到了旧快照）。

执行：并行调用的 observation 顺序要稳定（按名字排序），否则 监督微调（SFT） 在背顺序。所有 tool 返回仍用 mask 排除，不计入交叉熵损失（CE）。

## 失败

并行里一个失败、一个成功。数据要有：成功的结果留下、失败的重试或降级，不要整轮作废也不要假装全成功。见 `dt-tool-error-recover`。

写操作默认不并行，见 `dt-tool-write-confirm`。两个写入抢同一条日历记录，环境要有冲突示范。

## 追问

- **模型输出一个 list 就算并行？** 还要环境真的并跑。假并行（框架仍串行）会让延迟数据对不上产品。
- **端侧 3B 并行？** 示范仍按产品：能并就并。小模型更要短轨迹，并包能减轮次。
- **BFCL 并行题能训吗？** 当格式示范要先确认不在门禁。自己的 schema 上造同构图更稳。
