---
id: dt-gemini-rl-env
section: posttrain-data
order: 32
level: S
title: Gemini 2.5 技术报告怎么写 Agent 向的 RL 环境和奖励？
quick: "Agent 环境优先用测试、解释器和状态断言验证结果，模型生成式评分补充主观目标并校准。保存多步工具中间状态，审计改测试、空转和假装运行等行为。推理更长不能直接作为奖励，用户工具日志也不能默认进入训练。"
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

把奖励分成可验证结果与模型评分两部分。测试、解释器和状态断言先确认任务完成，模型评分再补充风格等规则无法覆盖的目标。环境需要支持多步动作和工具，并保存中间状态，才能审计是否钻了奖励规则的空子。Gemini 2.5 报告（arxiv 2507.06261）后训练段相对 1.5 写了：数据质量贯穿 监督微调（SFT）、奖励模型、强化学习（RL）；RL 算力加大；算法改了让长训更稳。然后：

> 这些改进让 Gemini 2.5 能从更多样、更复杂的 RL 环境学习，包括需要多步动作和工具使用的环境。

常见误区是：纯模型奖励当主门，或把「想得长」直接写成 $r$。agent 可能学会讨好评分模型，或生成更长推理链（CoT），却没有真正完成任务。

奖励明确写了两类：verifiable rewards 和 model-based generative rewards。可验证的是测试、解释器、状态断言。生成式是模型当 grader / 过程评委。Agent 主门仍应是前者。后者用来扩没有单元测试的任务，必须校准，见 OpenAI RFT 的模型 grader 和 Cosine 的「风格不能当前门」，`dt-agent-rft-recipe`。

Deep Think 博客：并行想多个假设再批判；另有 RL 技巧鼓励走这些更长推理路径。这是奖励设计，不是换 backbone。要和终局对错绑在一起。

Deep Think model card 还写了在 RE-Bench 一类环境里抽查轨迹、查 钻奖励规则的空子。Horizon 招聘启事把同一工作写成：造难题和能验证的 grader，在环境上训 Gemini，读轨迹看它真正学到什么，能迁移的再进产品。读轨迹是数据岗日常。

和 Silver / Sutton 的 Era of Experience 同一实验室传统：奖励由环境中的实际后果支持。Gemini 报告把「工具、多步」写进了公开配方。

苹果：可验证合成优先。生成式奖励只能当辅助，且教师是参考模型。用户工具日志不进基础模型。

## 追问

- **只有生成式奖励行不行？** 不行当主门。报告是两者一起。纯模型奖励，我会当辅助，agent 会讨好评委。
- **多步工具环境和数学 基于可验证奖励的强化学习（RLVR）？** 数学可以检查最终 boxed 答案；工具任务的 observation 来自环境，奖励可能到任务结束才给出。我会把中间状态存进数据，否则无法审计 hack。
- **读轨迹看什么？** 改测试、空转、背金补丁、假装跑测。和 `dt-swe-success-noise` 同一清单。
