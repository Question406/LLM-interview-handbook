---
id: dt-agent-env-is-data
section: posttrain-data
order: 18
level: S
title: Agent RL 的数据集是什么？为什么说「环境」替代了「jsonl」？
quick: >-
  Agent RL 的数据集是一批能装起来、能打分、能并行跑的任务环境：current policy 进去生成新 trajectories，grader
  看结果给奖励。手里的演示 jsonl 只是某个策略在某版环境上采的样，策略或环境一变就过时，主要拿来做 SFT
  冷启动。所以盘点时要记环境和奖励版本，训练和评测任务分开。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'Karpathy on X: in the RL era it is environments'
    url: 'https://x.com/karpathy/status/1960803117689397543'
    type: secondary
  - title: Welcome to the Era of Experience (Silver & Sutton)
    url: >-
      https://storage.googleapis.com/deepmind-media/Era-of-Experience%20/The%20Era%20of%20Experience%20Paper.pdf
    type: primary
  - title: LLM Powered Autonomous Agents (Lilian Weng)
    url: 'https://lilianweng.github.io/posts/2023-06-23-agent/'
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Agent RL 的数据集是一批可执行的环境：给一个任务，模型进去和环境交互，grader 检查结果给奖励。手里已有的 SFT trajectories 可以拿来冷启动，在线探索还是得让 current policy 自己去环境里跑，攒再多 ReAct 演示也给不了这一点。

举个例子，有人说「我们有 80 万条 agent trajectories」。可如果没记下这些 trajectories 是哪个策略、在哪一版环境上采的，别人就没法判断它们今天还能不能用。

jsonl 会过期，是因为 RL 要的是 current policy 自己的 trajectories。一份 jsonl 是某个策略在某一版环境上采出来的，策略一更新，旧 trajectories 就成了 off-policy 数据，慢慢过期（`dt-onpolicy-pref` 讲过这件事）。环境不会这样过期，同一个任务可以让新策略重新跑一遍，grader 重新打分。

这个说法有公开出处。Karpathy 把几个阶段概括成：pre-training 缺文本，SFT 缺对话，RL 缺环境，还点名了 Prime Intellect 的 Environments Hub 和 `verifiers`（LLM 版的 Gym）。

所以盘点数据资产时，我会报这几件事：有多少能装起来的环境，能不能在容器里复现，奖励是不是确定的，训练和评测任务有没有隔开。

有人参与的工具平台也算环境。AFM 2025 报告里的工具平台由 reference model、执行环境和人工回滚组成，就是人在环里的环境。上 Agent RL 减少的是每次交互对人工操作的依赖，环境和 grader 都还在。

## 追问

**Karpathy 自己看好这条路吗？**
看好环境，对 reward function 本身不太乐观，原话是 sus。不过他承认环境是现在能规模化的练习场。

**还有谁讲过类似的观点？**
Silver 和 Sutton 的 Era of Experience 讲的是同一件事：观察来自真实交互，奖励来自能核对的结果，人预先写好的短片段退到次要位置。更早一点，Lilian Weng 2023 年把 agent 拆成规划、记忆、工具三块，RL 数据要做的就是把这三块放进一个能执行的循环。

**一个环境具体要包含什么？**
Will Brown 把环境定义成可复用的「任务 + harness + 奖励」，既能评也能训。具体怎么打包见 `dt-agent-env-stack`。

**没有环境，只有成功的 diff，怎么办？**
当 SFT 或模仿学习的数据用，不拿去做 RL。SWE-RL 用和 oracle patch 的相似度当奖励，功能等价但写法不同的解就会被压低分数，见 `dt-agent-reward-spec`。

**能拿当年 Gym 的 cartpole 类比吗？**
可以，类比完再讲差别：现在的任务是 SWE、终端、浏览器，grader 看的是测试结果和环境状态。
