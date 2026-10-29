---
id: dt-agent-env-stack
section: posttrain-data
order: 22
level: S
title: Agent 环境要打包成什么，才能既评又训？
quick: >-
  打包成一个能 pip install 的任务环境，里面有任务说明和初始资源、把 tool calls 接到真实系统的 harness、给结果打分的
  rubric。三样都要能安装、能版本化，训练和评测共用同一套执行和评分逻辑，两边的目标才一致。只有 prompt 模板、没有可执行动作和
  scorer，撑不起 Agent RL。
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
  - title: 'Will Brown: RL Environments at Scale'
    url: 'https://ai.engineer/talks/rl-environments-at-scale'
    type: secondary
  - title: Prime Intellect Environments Hub
    url: 'https://www.primeintellect.ai/blog/environments'
    type: secondary
  - title: Environments Hub docs
    url: 'https://docs.primeintellect.ai/tutorials-environments/environments'
    type: secondary
  - title: verifiers (Prime Intellect)
    url: 'https://github.com/PrimeIntellect-ai/verifiers'
    type: secondary
  - title: 'Karpathy on X: in the RL era it is environments'
    url: 'https://x.com/karpathy/status/1960803117689397543'
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

交付一个能 `pip install` 的任务包，里面放三样东西：任务、执行框架（harness）和评分规则（rubric）。训练和评测共用执行和评分逻辑，区别只在用哪个策略跑、奖励要不要回传去更新模型。这个拆法来自 Will Brown 和 Prime Intellect，Karpathy 点名的也正是 Environments Hub 加 `verifiers`。

举个例子，评测用 pytest 跑 hidden tests，训练图省事改成「输出里包含某个字符串就给分」。两个 grader 奖励的是不同的行为，训练分一路涨，评测分不一定跟着涨。所以评分逻辑必须是同一份。缺了 harness 更糟，所谓「agent 数据集」只是一堆文本，模型的动作改变不了任何东西，没法做 RL。

三样东西各管一块。任务部分提供说明、初始状态和资源，比如仓库快照、网页镜像、fake API，环境要能从这些内容重新启动，rollout 才能复现。Harness 把模型的 tool calls 接到 shell、浏览器和文件系统，让动作真的改变环境；超时、沙箱、重试也由 harness 在代码里控制，光写在 prompt 里约束不住模型。Rubric 定最终怎么打分，比如 hidden tests 权重 1、格式分 0.05、日志项权重 0。

`verifiers` 把这套结构接到常见的 RL trainer 上。SkyRL 也是一样的思路，把环境服务和训练拆开，见 `dt-agent-scale-env`。

数据组交付时，我会记下镜像哈希、依赖锁、rubric 版本和任务 ID，拿这些键去关联 rollout 日志。harness 升级要当成数据集版本 bump 来处理，否则昨天成功的 trajectories 今天复放就会失败。

## 追问

**只有 prompt 模板算环境吗？**
不算。没有副作用，也没有 grader，它只是 SFT 模板。

**一个环境就对应一个任务吗？**
一个环境可以挂很多任务：harness 共享，任务是实例。比如 OSWorld 一个电脑镜像对应很多条 instruction。

**开源 Hub 能直接当训练池吗？**
能用来对齐格式和做评测。拿来训练的话，我会另外确认许可，并留出 holdout，见 `dt-license-is-quality`、`dt-agent-verified-stale`。

**有人工回滚的工具平台，离 RL 环境还差多少？**
差得不多，这三件套它已经有了，上 RL 主要是把人从热路径上拿掉。AFM 2025 报告里的工具平台就由 reference model、执行环境和人工回滚组成。
