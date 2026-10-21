---
id: dt-agent-env-is-data
section: posttrain-data
order: 18
level: S
title: Agent RL 的数据集是什么？为什么说「环境」替代了「jsonl」？
quick: "Agent RL 的数据资产是可安装、可评分、可并行的任务环境：策略在里面生成新轨迹，grader 验证结果给奖励。已有演示 jsonl 只是某个策略在某版环境上的采样，策略或环境一变就过时，主要用于 SFT 冷启动。所以要记录环境和奖励版本，并隔离训练与评测任务。"
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

Agent RL 的「数据集」是可执行的环境：给定任务，模型和环境交互，grader 检查结果并给奖励。已有的 SFT 轨迹可以拿来冷启动；在线探索需要当前策略自己去环境里跑，光攒大量 ReAct 演示提供不了这一点。

## 为什么 jsonl 会过期

一份 jsonl 是某个策略在某一版环境上采出来的样本。RL 要的是当前策略自己的轨迹，策略一更新，旧轨迹就成了 off-policy 数据，逐渐过期（见 `dt-onpolicy-pref`）。环境不会这样过期：同一个任务可以让新策略重新跑，grader 重新打分。

这个说法有公开出处。Karpathy 把几个阶段概括为：预训练缺文本，SFT 缺对话，RL 缺环境，并点名了 Prime Intellect 的 Environments Hub 和 `verifiers`（LLM 版 Gym）。他对奖励函数本身并不乐观（原话是 sus），但承认环境是现在能规模化的练习场。Silver 和 Sutton 的 Era of Experience 讲的是同一件事：观察来自真实交互，奖励来自可核对的结果，人预先写好的短片段退居次要。Lilian Weng 2023 年把 agent 拆成规划、记忆、工具三块，RL 数据要做的就是把这三块放进一个可执行的循环。Will Brown 后来把环境定义成可复用的「任务 + harness + 奖励」，既能评也能训，具体怎么打包见 `dt-agent-env-stack`。

有人参与的工具平台本身也算环境。AFM 2025 报告描述的工具平台由参考模型、执行环境和人工回滚组成，就是人在环里的环境。Agent RL 减少的是每次交互中对人工操作的依赖，环境和 grader 都留下来。

## 盘点数据资产时报什么

我会报：有多少可安装的环境、能否在容器里复现、奖励是否确定、训练和评测任务是否隔离。只说「有 80 万条轨迹」却没有记录环境版本，别人无法判断这些轨迹现在还能不能用。

## 追问

- **没有环境，只有成功的 diff，怎么办？** 当 SFT 或模仿学习用，不当 RL。SWE-RL 甚至用和 oracle patch 的相似度当奖励，结果功能等价但写法不同的解会被压低分数，见 `dt-agent-reward-spec`。
- **能拿当年 Gym 的 cartpole 类比吗？** 可以接这个类比，再讲清差别：现在的任务是 SWE、终端、浏览器，grader 看的是测试结果和环境状态。
