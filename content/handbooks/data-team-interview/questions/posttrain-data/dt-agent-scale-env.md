---
id: dt-agent-scale-env
section: posttrain-data
order: 23
level: S
title: Agent RL 怎么把环境扩到能真正跑起来？Qwen 和 SkyRL 各做了什么？
quick: "先让单个任务在干净容器里稳定复现，再加并行环境；Agent RL 的瓶颈在环境规模。Qwen 同时跑 2 万个独立环境，SkyRL 用异步执行、任务调度和工具服务把吞吐提到朴素实现的约 4 到 5 倍。扩之前先查超时、依赖和文件系统隔离。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Infrastructure
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Qwen3-Coder
    url: https://qwenlm.github.io/blog/qwen3-coder/
    type: primary
  - title: SkyRL-v0
    url: https://novasky-ai.notion.site/SkyRL-v0-Train-Real-World-Long-Horizon-Agents-via-Reinforcement-Learning-1e38f0016b9d80668206c7a9c89d6205
    type: secondary
  - title: SkyRL-Agent
    url: https://arxiv.org/abs/2511.16108
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先回答能稳定运行多少个环境、挂起比例多高，再谈 PPO。并行环境数、每条轨迹的长度、失败怎么隔离，这些都比算法细节更早需要解决。Qwen 博客也把强化学习（RL）的瓶颈写成 environment scaling。

## 为什么环境先于算法

单环境还复现不了就直接开 2 万并行，问题会被放大：环境死掉、依赖互相串、磁盘打满，采样轨迹（rollout）就变成噪声，奖励里分不清是模型的错还是环境的错。

## 公开配方怎么扩

**Qwen3-Coder。** 后训练做了 long-horizon Agent RL：多轮规划、调用工具、读反馈。他们借助阿里云同时跑 2 万个独立环境。这个数字说明 coding RL 需要大量能同时稳定运行的沙箱，Qwen 用这个量级来说明 coding agent 的环境成本，它算不上入门门槛。

**SkyRL。** NovaSky 的 SkyRL-v0（搭在 VeRL 和 OpenHands 上）和后续的 SkyRL-Agent，做的是异步多轮 rollout、通用工具和可扩展的环境执行，报告相对朴素实现约 4 到 5 倍吞吐。SkyRL-Agent 进一步把 dispatcher 和工具（包括 AST 搜索）写进配方，还接入了 Prime Intellect Environments Hub 和 mini-SWE-agent。它把环境服务和训练拆开：同机部署适合演示，规模一大就容易争用磁盘。

所以面试里讲扩展，我会讲「环境副本数」和「每个副本的任务队列」。只说「开了 GRPO」，听不出环境能不能撑住。造题配方见 `dt-agent-tmax-synth`。

## 扩之前的清单

- 单个任务能否在干净容器里复现；
- 超时和 OOM 是否会记成明确的失败状态，不会一直挂着；
- 并行时文件系统、端口、缓存是否隔离；
- 失败的环境会不会污染邻居。

这些不通过，扩到 2 万并行也只是同时运行一大批不稳定的环境。我会报实际能稳定跑的副本数和 hang 率，峰值并行数只作参考。

## 追问

- **异步 rollout 带来的 off-policy 怎么办？** 记录环境版本和策略版本，过期轨迹降权或丢掉，见 `dt-onpolicy-pref`。
