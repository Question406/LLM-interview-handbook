---
id: dt-agent-env-is-data
section: posttrain-data
order: 18
level: S
title: Agent RL 的数据集是什么？为什么说「环境」替代了「jsonl」？
quick: "Agent RL 的数据资产是可安装、可评分、可并行的任务环境。策略在其中生成新轨迹，评分器验证结果；已有演示主要用于 SFT 冷启动。轨迹会随策略和环境变化而过时，所以需要记录环境、奖励版本，并隔离训练与评测任务。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Environment
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Karpathy on X: in the RL era it is environments"
    url: https://x.com/karpathy/status/1960803117689397543
    type: secondary
  - title: Welcome to the Era of Experience (Silver & Sutton)
    url: https://storage.googleapis.com/deepmind-media/Era-of-Experience%20/The%20Era%20of%20Experience%20Paper.pdf
    type: primary
  - title: LLM Powered Autonomous Agents (Lilian Weng)
    url: https://lilianweng.github.io/posts/2023-06-23-agent/
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Agent RL 需要可执行环境：给定任务，模型与环境交互，grader 检查结果并给奖励。已有的 SFT 轨迹可用于冷启动，但只收集大量 ReAct 演示，还没有提供当前策略在线探索所需的环境。

不这么选的理由：jsonl 是某一策略在某一版环境上的采样，策略一换就过期，见 `dt-onpolicy-pref`。公开锚点里 Karpathy 把时代切成预训练缺文本、SFT 缺对话、RL 缺环境，并点了 Prime Intellect 的 Environments Hub 和 `verifiers`（LLM 版 Gym）。他对奖励函数本身不乐观（sus），但承认环境是现在能扩的练习场。Silver / Sutton 的 Era of Experience 也是观察来自真实交互，奖励来自可核对的结果，不再只靠人预先写好的短片段。Lilian Weng 2023 把 agent 拆成规划、记忆、工具；RL 数据要把这三块放进可执行循环。Will Brown 后来把环境说成可复用的「任务 + harness + 奖励」，既能评也能训，见 `dt-agent-env-stack`。

## 我会怎么报家当

报告有多少可安装环境、能否在容器中复现、奖励是否确定、训练与评测任务是否隔离。仅说有 80 万条轨迹，却不记录环境版本，无法判断这些轨迹还能否使用。

苹果：AFM 的工具平台（参考模型 + 执行环境 + 人回滚）已经是环境，只是人在环。Agent RL 减少每次交互中对人工操作的依赖，留下环境和 grader。许可环境里的执行反馈可以进；用户日志默认不进基础模型，产品用户会话也不要叫成 RL 环境。

## 追问

- **没有环境，只有成功 diff？** 我会当 SFT / 模仿，不当 RL。SWE-RL 甚至用和 oracle patch 的相似度当奖励，功能等价的解会被压低，见 `dt-agent-reward-spec`。
- **Gym 当年的 cartpole 能类比吗？** 我会接这个类比，差别讲清楚：现在任务是 SWE、终端、浏览器，grader 是测试和状态，不是游戏分数。
- **苹果怎么讲？** 我会讲许可环境里的执行反馈，不把产品用户会话说成 RL 环境。
