---
id: dt-agent-env-stack
section: posttrain-data
order: 22
level: S
title: Agent 环境要打包成什么，才能既评又训？
quick: "任务环境包含任务说明与初始资源、连接工具动作的 harness，以及判断结果的 rubric。三者都可安装、可版本化，训练与评测共用逻辑。只有 prompt 模板、没有可执行动作和评分器，还不能支持 Agent RL。"
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
  - title: "Will Brown: RL Environments at Scale"
    url: https://ai.engineer/talks/rl-environments-at-scale
    type: secondary
  - title: Prime Intellect Environments Hub
    url: https://www.primeintellect.ai/blog/environments
    type: secondary
  - title: Environments Hub docs
    url: https://docs.primeintellect.ai/tutorials-environments/environments
    type: secondary
  - title: verifiers (Prime Intellect)
    url: https://github.com/PrimeIntellect-ai/verifiers
    type: secondary
  - title: "Karpathy on X: in the RL era it is environments"
    url: https://x.com/karpathy/status/1960803117689397543
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

可以交付能 `pip install` 的任务包，包含任务、执行框架（harness）和评分规则（rubric）。训练与评测共用执行和评分逻辑，区别是使用的策略，以及是否把奖励回传用于更新。公开拆法是 Will Brown / Prime Intellect 的任务、harness、rubric；Karpathy 点名的就是 Environments Hub + `verifiers`。

常见误区是：缺 harness 的「agent 数据集」无法 强化学习（RL）。评测用 pytest、训练用字符串包含，两边 grader 会打架。

## 三件套

任务部分提供说明、初始状态和资源，例如仓库快照、网页镜像、fake API。环境必须能从这些内容重新启动。

Harness 将模型工具调用接到 shell、浏览器和文件系统，让动作真正改变环境。超时、沙箱、重试也由执行框架控制，不只写在 prompt 里。

Rubric 定义最终如何评分。例如隐藏测试权重 1、格式分 0.05、日志项权重 0。训练和评测用同一套规则，避免目标不一致。

`verifiers` 把这套接到常见 RL trainer。SkyRL 也是同一想法：环境服务和训练解耦，见 `dt-agent-scale-env`。

## 数据组交什么

记录镜像哈希、依赖锁、rubric 版本和任务 ID，并用这些键关联 rollout 日志。harness 升级要当数据集版本 bump，不然昨天的成功轨迹今天复放失败。

苹果：AFM 的工具平台已经有参考模型、执行环境、人回滚。RL 只是把人从热路径拿掉，三件套还在。用户对话默认不进这套。开源 Hub 能当格式和评测；训练还要许可和 holdout，见 `dt-license-is-quality`、`dt-agent-verified-stale`。

## 追问

- **只有 prompt 模板算环境吗？** 不算。没有副作用、没有 grader，只是 监督微调（SFT） 模板。
- **一个环境多个任务？** 对。harness 共享，任务是实例。OSWorld 一个电脑镜像很多 instruction。
- **开源 Hub 能当训练池吗？** 能当格式和评测。训练我会另要许可和 holdout。
