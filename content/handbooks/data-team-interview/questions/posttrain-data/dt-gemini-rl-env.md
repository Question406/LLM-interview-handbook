---
id: dt-gemini-rl-env
section: posttrain-data
order: 32
level: S
title: Gemini 2.5 技术报告怎么写 Agent 向的 RL 环境和奖励？
quick: "报告把奖励分成两类：可验证奖励（测试、解释器、状态断言）当主门，模型生成式评分补充规则覆盖不到的目标，并且要校准。环境要支持多步动作和工具，并保存中间状态，才能审计改测试、空转、假装运行这类 hack。推理长度要和最终对错绑在一起，直接奖励「想得长」，模型会写出更长的推理却没完成任务。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - DeepMind
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Gemini 2.5 technical report"
    url: https://arxiv.org/abs/2507.06261
    type: primary
  - title: Gemini 2.5 Deep Think
    url: https://blog.google/products-and-platforms/products/gemini/gemini-2-5-deep-think/
    type: secondary
  - title: Welcome to the Era of Experience (Silver & Sutton)
    url: http://incompleteideas.net/papers/TheEraOfExperience.pdf
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Gemini 2.5 报告把奖励分成两类：可验证奖励和模型生成式奖励。Agent 环境的主门应该是前者，也就是用测试、解释器和状态断言先确认任务真的完成；模型评分再补充风格这类规则覆盖不到的目标。环境还要支持多步动作和工具，并保存中间状态，否则没法审计模型有没有钻奖励规则的空子。

## 报告公开写了什么

Gemini 2.5 报告（arxiv 2507.06261）的后训练部分，相对 1.5 写了三处变化：数据质量贯穿监督微调（SFT）、奖励模型和强化学习（RL）；RL 算力加大；算法改进让长时间训练更稳。接着是这句：

> 这些改进让 Gemini 2.5 能从更多样、更复杂的 RL 环境学习，包括需要多步动作和工具使用的环境。

这和 Silver / Sutton 在 Era of Experience 里讲的是同一个实验室传统：奖励要由环境里的实际后果支撑。Gemini 报告把「工具、多步」明确写进了公开配方。

## 为什么可验证奖励要当主门

如果纯靠模型奖励当主门，或者把「想得长」直接写进 $r$，agent 可能学会讨好评分模型，或者生成更长的推理链（CoT），却没有真正完成任务。可验证奖励只看结果，测试过没过、状态对不对，很难被讨好。

生成式奖励的作用是扩展到没有单元测试的任务，用模型当 grader 或过程评委。它必须校准，参考 OpenAI RFT 的模型 grader，以及 Cosine 把风格放在正确性门禁之后的做法，见 `dt-agent-rft-recipe`。

Deep Think 博客的例子也说明了这一点。它并行生成多个假设再相互批判，另外用 RL 技巧鼓励模型走这些更长的推理路径。这是奖励设计上的改动，长推理的奖励要和最终对错绑在一起。

## 读轨迹是日常工作

Deep Think model card 写了，他们在 RE-Bench 一类环境里抽查轨迹，检查有没有钻奖励规则的空子。Horizon 的招聘启事把同一类工作描述为：造难题和能验证的 grader，在环境上训 Gemini，读轨迹看它真正学到了什么，能迁移的再放进产品。对数据岗来说，读轨迹就是日常。

## 追问

- **只用生成式奖励行不行？** 不能当主门。报告里是两类一起用。纯模型奖励我只当辅助，否则 agent 会去讨好评委。
- **多步工具环境和数学的基于可验证奖励的强化学习（RLVR）有什么不同？** 数学可以只检查最终 boxed 答案；工具任务的 observation 来自环境，奖励可能要到任务结束才给。所以我会把中间状态存进数据，不然无法审计 hack。
- **读轨迹具体看什么？** 改测试、空转、背金标准补丁、假装跑了测试。和 `dt-swe-success-noise` 是同一份清单。
