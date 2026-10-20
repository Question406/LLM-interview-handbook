---
id: dt-shunyu-second-half
section: posttrain-data
order: 28
level: S
title: OpenAI 的 Shunyu Yao 把 Agent RL 配方写成什么？数据岗听哪一句？
quick: "先有语言预训练提供的能力，再有可执行环境和可计算的结果奖励，最后选择训练算法。数据岗主要负责定义任务、构造环境和降低评分噪声。只换 PPO 或 GRPO 变体，解决不了任务与奖励本身的问题。"
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

可以先解释语言预训练提供的能力，再解释环境怎样让模型尝试动作并收到反馈，推理也可以算动作。o 系列、R1、deep research 和电脑使用的公开讨论都围绕这些要素。算法也影响训练，但只讲从 REINFORCE 换到 GRPO，不足以解释数据方案。

常见误区是：把「我们换了 DAPO」当数据方案。没有先验，环境转不动。公开锚点是 Yao 2025-04 的 The Second Half（斯坦福 224N / Columbia 的 talk 改写成博客）。OpenAI 早年 Gym / Universe 把电脑当游戏，缺语言模型先验，域间不迁移。和 Karpathy、Silver / Sutton 对齐，见 `dt-agent-env-is-data`。

## 数据岗听什么

任务定义比算法难。评价和「该训什么」变成中心。

奖励应基于任务结果，能自动计算，而且重复运行要稳定。过程奖励和偏好奖励容易被 hack。这和 Cosine 先过测试再打风格是同一句，见 `dt-agent-rft-recipe`。

评测假设会害训练数据。他点了两条：评测默认全自动、任务 i.i.d.。真实客服有人在环（τ-bench 用户模拟），真实 SWE 会在同一个仓库里变熟。训练池如果每条 issue 冷启动、互不记忆，和线上不是同一个 MDP。

utility problem。IMO / IOI 金奖，GDP 没动。门禁涨了不等于产品有用。Agent 数据要能在真实环境里被 grader 打分，不要只洗公开榜，见 `dt-agent-verified-stale`。

苹果：许可环境、可验证合成、参考模型当教师。用户会话默认不进基础模型。Yao 的「人在环评测」在苹果侧是研究集和工具平台回滚，不是拿 Siri 日志做 强化学习（RL）。

## 追问

- **那算法完全不管？** 管稳定性、吞吐。我会把优先级排成先验、环境、奖励，再是算法。
- **推理当动作会不会把思考写得很长来刷奖励？** 会。我会把结果奖励绑终局 grader，不要把 文本处理单位（token） 数当 $r$。
- **和 Silver 的 Era of Experience？** Silver 要环境有实际证据支持的奖励。Yao 补了语言先验和「推理动作」。两篇一起用，不当 journal club 对照。
