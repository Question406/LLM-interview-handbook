---
id: dt-shunyu-second-half
section: posttrain-data
order: 28
level: S
title: OpenAI 的 Shunyu Yao 把 Agent RL 配方写成什么？数据岗听哪一句？
quick: "配方的顺序是：先有语言预训练给的先验，再有可执行环境和可自动计算的结果奖励，最后才是算法。数据岗该听的是「任务定义比算法难」：定义任务、构造环境、降低评分噪声都是数据岗的活；只把 PPO 换成 GRPO 变体，解决不了任务和奖励本身的问题。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "The Second Half (Shunyu Yao)"
    url: https://ysymyth.github.io/The-Second-Half/
    type: primary
  - title: Welcome to the Era of Experience (Silver & Sutton)
    url: http://incompleteideas.net/papers/TheEraOfExperience.pdf
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Yao 的配方按重要性排是：先有语言预训练提供的先验，再有环境让模型尝试动作、收到反馈（推理本身也可以算动作），最后才是算法。数据岗该听的一句是「任务定义比算法难」。评价什么、该训什么成了中心问题，而这正是数据岗在做的事：定义任务、搭环境、降低评分噪声。

## 为什么先验和环境排在算法前面

出处是 Yao 2025-04 的 The Second Half，由他在斯坦福 224N / Columbia 的 talk 改写成博客。o 系列、R1、deep research 和电脑使用的公开讨论都围绕这几个要素展开。

反面例子是 OpenAI 早年的 Gym / Universe：把电脑当成游戏来做 RL，但没有语言模型的先验，学到的东西在不同领域之间不迁移。没有先验，环境就转不起来。所以「我们换成了 DAPO」回答不了数据方案的问题。算法会影响训练，可从 REINFORCE 换到 GRPO，说明不了题目和奖励从哪来。这个判断和 Karpathy、Silver / Sutton 的观点一致，见 `dt-agent-env-is-data`。

## 数据岗具体听什么

第一，奖励要基于任务结果，能自动计算，重复运行时结果稳定。过程奖励和偏好奖励容易被 hack。这和 Cosine 先过测试再评风格是一个意思，见 `dt-agent-rft-recipe`。

第二，评测里的假设会带坏训练数据。他点了两个假设：评测默认全自动，任务之间 i.i.d.。可真实客服是有人在环的（τ-bench 因此用用户模拟），真实 SWE 中模型会在同一个仓库里越做越熟。如果训练池里每条 issue 都冷启动、互不记忆，它和线上就不是同一个 MDP。

第三，utility problem。模型拿了 IMO / IOI 金奖，GDP 没动，门禁涨了，模型未必更有用。Agent 数据要能在真实环境里被 grader 打分，只围着公开榜单洗数据，榜单分数和真实能力会越拉越开，见 `dt-agent-verified-stale`。

## 追问

- **那算法完全不用管？** 要管，它决定稳定性和吞吐。我的优先级是先验、环境、奖励，然后才是算法。
- **推理算动作，模型会不会把思考写得很长来刷奖励？** 会。所以结果奖励要绑定终局 grader，不能把文本处理单位（token）数当 $r$。
- **和 Silver 的 Era of Experience 是什么关系？** Silver 要求奖励有环境里的实际证据支撑，Yao 补上了语言先验和「推理即动作」。两篇放在一起用，不必当 journal club 里的对照来讲。
