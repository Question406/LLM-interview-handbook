---
id: dt-agent-fireact
section: posttrain-data
order: 13
level: A
title: Agent SFT：500 条 GPT-4 轨迹就够吗，多样从哪来？
quick: "几百条可回放的成功轨迹够教模型调用格式和何时停止，但泛化不够。多样性来自不同的任务、格式和教师，同一条 ReAct 复制再多遍也学不到新东西。FireAct 的约 500 条适用于短程、易验证的搜索 QA，SWE、GUI 或多轮客服需要更多可执行任务。"
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

用监督微调（SFT）教模型基本的调用格式和何时停止，几百条可回放的轨迹就能起步。要进一步提升，靠的是任务和提示格式的多样性，把同一条 ReAct 复制 10 万遍没有用。500 条这个数只适用于短程、grader 清楚的任务。

## 为什么几百条就能涨

FireAct 的结果是：Llama2-7B 只用约 500 条 GPT-4 在 HotpotQA 上搜出来的轨迹做微调，效果就有提升。Zeng 等人的 AgentTuning 用混合的 agent 任务做了同样的事。这和 LIMA 的结论相似，少量高质量数据就能教会格式，区别是这里的 grader 是环境，见 `dt-lima-vs-scale`。

但只用一个环境、一个教师、一种格式训练，模型学到的很窄，换个工具名或换个用户模拟器就可能失效。

## 多样性从哪来

- **任务**：检索 QA、改日历、修代码、逛网页，HotpotQA 只是其中一类。
- **格式**：ReAct 文本、规范的 function call、并行调用都要有。只训一种格式，工具 schema 的字段或类型要求一变，模型就可能不会调用了，见 `dt-tool-alias`。
- **教师**：用多个教师，或同一个教师的多种温度。只有单一 GPT-4 文风，学生会死记「先写 Thought:」这类套路。
- **失败轨迹**：FireAct 的主结果偏向成功轨迹，错误恢复要另外配数据，见 `dt-tool-error-recover`。

## 500 条的边界

搜索 QA 这种短程、grader 清楚的任务，几百条够用。SWE、GUI、多轮客服不够：SWE-Gym 要几千个可执行任务，见 `dt-agent-swegym`。

轨迹还必须可回放。教师当时拿到的搜索结果要存下来，否则 SFT 学的是过期的 snippet。训练时也要屏蔽 observation 部分的损失，不让模型学着去生成工具结果。

## 追问

- **few-shot 已经能跑，为什么还要 SFT？** 小模型的上下文装不下长示范，所以我会微调，把格式和停止时机写进权重。
- **SFT 和强化学习（RL）谁先？** 先用 SFT 冷启动格式，再上环境奖励。R1 也是这个顺序。
