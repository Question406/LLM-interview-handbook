---
id: dt-agent-fireact
section: posttrain-data
order: 13
level: A
title: Agent SFT：500 条 GPT-4 轨迹就够吗，多样从哪来？
quick: "可以用几百条可回放的成功轨迹教模型调用格式和停止条件，但多样性要来自不同任务、格式和教师。FireAct 的约 500 条适用于较短、易验证的搜索 QA，不能直接推到 SWE、GUI 或多轮客服任务。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - SFT
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "FireAct: Toward Language Agent Fine-tuning"
    url: https://arxiv.org/abs/2310.05915
    type: primary
  - title: "AgentTuning: Enabling Generalized Agent Abilities for LLMs"
    url: https://arxiv.org/abs/2310.12823
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先用监督微调（SFT）教模型基本调用格式和何时停止。几百条可回放轨迹可以作起点，进一步改善要增加任务和提示格式的多样性，不能靠把同一条 ReAct 复制 10 万遍。公开锚点是 FireAct：Llama2-7B 用约 500 条 GPT-4 搜出来的 HotpotQA 轨迹就能涨。Zeng 等 AgentTuning 用混合 agent 任务做同样的事。这和 LIMA 像，但 grader 是环境，见 `dt-lima-vs-scale`。

只用一个环境、一个教师和一种格式训练，模型可能在换工具名或用户模拟器后失效。500 条也不是通用数量，SWE、GUI 和多轮客服通常需要更多覆盖。

## 多样指什么

任务：检索 QA、改日历、修代码、逛网页，不要只有 HotpotQA。

格式：ReAct 文本、规范 function call、并行调用。只训练一种格式，产品 schema 的字段和类型要求一变，模型就可能不会调用，见 `dt-tool-alias`。

教师：多个教师或同一教师多种温度。单一 GPT-4 文风，学生会背「先 Thought:」。

失败：FireAct 主结果偏成功轨迹。要另配 `dt-tool-error-recover`。

## 500 条的边界

搜索 QA 这种短程、grader 清楚的，几百条可以。SWE、GUI、多轮客服不是。SWE-Gym 要几千可执行任务，见 `dt-agent-swegym`。

轨迹要可回放。教师当时的搜索结果要存下来，否则 SFT 在背过期 snippet。训练时仍要屏蔽 observation 的损失，不让模型学习生成工具结果。

苹果：用户真实 agent 日志默认不进基础模型。用许可环境或验证合成。端侧更吃「微调把格式写进权重」这一套，因为小模型 few-shot 吃不下长示范。

## 追问

- **few-shot 已经能跑，为什么还 SFT？** 小模型 few-shot 吃不下长示范。我会微调，把格式和何时停写进权重。端侧更吃这一套。
- **和 强化学习（RL） 谁先？** 先 SFT 冷启动格式，再环境奖励。R1 也是这个顺序。
- **用户真实 agent 日志？** 苹果默认不进基础模型。我会用环境合成。
