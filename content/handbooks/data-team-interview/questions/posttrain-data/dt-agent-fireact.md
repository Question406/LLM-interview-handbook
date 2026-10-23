---
id: dt-agent-fireact
section: posttrain-data
order: 13
level: A
title: Agent SFT：500 条 GPT-4 轨迹就够吗，多样从哪来？
quick: "几百条可回放的成功轨迹，够教会模型调用格式和什么时候停，泛化还不够。多样性来自不同的任务、格式和教师，同一条 ReAct 复制再多遍也学不到新东西。FireAct 的约 500 条适合短程、好验证的搜索 QA，SWE、GUI、多轮客服要更多可执行任务。"
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

几百条可回放的轨迹够教模型基本的调用格式和什么时候停，再往上涨要靠任务和格式的多样性，同一条 ReAct 复制 10 万遍没有用。500 条这个数只适用于短程、grader 清楚的任务。

这个数来自 FireAct：Llama2-7B 只用约 500 条 GPT-4 在 HotpotQA 上搜出来的轨迹做监督微调（SFT），效果就有提升。道理和 LIMA 差不多，少量高质量数据就能教会格式，区别是这里的 grader 是环境（见 `dt-lima-vs-scale`）。

问题在于学到的东西很窄。只用一个环境、一个教师、一种格式训，换个工具名或换个用户模拟器就可能失效。比如训练数据全是 ReAct 文本，上线后工具 schema 的字段或类型要求一变，模型可能就不会调用了（见 `dt-tool-alias`）。

所以我会从几个方向补多样性。任务上，检索 QA、改日历、修代码、逛网页都要有，HotpotQA 只是其中一类。格式上，ReAct 文本、规范的 function call、并行调用都要覆盖。教师上，用多个教师，或者同一个教师的不同温度；只有单一 GPT-4 文风，学生会死记「先写 Thought:」这类套路。FireAct 的主结果偏向成功轨迹，错误恢复要另外配数据（见 `dt-tool-error-recover`）。

轨迹本身还要能回放。教师当时拿到的搜索结果要存下来，否则 SFT 学的是过期的 snippet。训练时也要把 observation 部分的损失屏蔽掉，不让模型学着去生成工具结果。

## 追问

**500 条放到 SWE 或 GUI 上够吗？**
不够。搜索 QA 短程、grader 清楚，几百条够用；SWE、GUI、多轮客服要多得多，SWE-Gym 用了几千个可执行任务，见 `dt-agent-swegym`。

**除了 FireAct 还有什么可以参考？**
Zeng 等人的 AgentTuning 用混合的 agent 任务做了同样的事，可以和 FireAct 只用 HotpotQA 的设置对照着讲。

**few-shot 已经能跑，为什么还要 SFT？**
小模型的上下文装不下长示范，所以我会微调，把格式和停止时机写进权重。

**SFT 和强化学习（RL）谁先？**
先用 SFT 冷启动格式，再上环境奖励。R1 也是这个顺序。
