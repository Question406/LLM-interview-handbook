---
id: dt-agent-scale-env
section: posttrain-data
order: 23
level: S
title: Agent RL 怎么把环境扩到能真正跑起来？Qwen 和 SkyRL 各做了什么？
quick: >-
  先让单个任务在干净容器里稳定复现，再加并行环境，Agent RL 的瓶颈在环境规模。Qwen 同时跑 2 万个独立环境，SkyRL
  用异步执行、任务调度和工具服务把 throughput 提到朴素实现的约 4 到 5 倍。扩之前先查超时、依赖和文件系统隔离。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Qwen3-Coder
    url: 'https://qwenlm.github.io/blog/qwen3-coder/'
    type: primary
  - title: SkyRL-v0
    url: >-
      https://novasky-ai.notion.site/SkyRL-v0-Train-Real-World-Long-Horizon-Agents-via-Reinforcement-Learning-1e38f0016b9d80668206c7a9c89d6205
    type: secondary
  - title: SkyRL-Agent
    url: 'https://arxiv.org/abs/2511.16108'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先回答能稳定运行多少个环境、挂起比例多高，再谈 PPO。并行环境数、每条 trajectories 多长、失败怎么隔离，这些都比算法细节更早要解决。Qwen 博客也把 RL 的瓶颈写成 environment scaling。

举个例子，单个任务在干净容器里还复现不了，就直接开 2 万并行。环境死掉、依赖互相串、磁盘打满，rollout 就变成噪声，奖励里分不清是模型的错还是环境的错。

所以扩之前我会先过一遍：单个任务能不能在干净容器里复现；超时和 OOM 会不会记成明确的失败状态，不会一直挂着；并行时文件系统、端口、缓存有没有隔开；一个环境挂了会不会 contamination 邻居。这几条不过，扩到 2 万并行也只是同时跑一大批不稳定的环境。

公开配方里有两个参照。Qwen3-Coder post-training 做了 long-horizon Agent RL，多轮规划、调用工具、读反馈，借助阿里云同时跑 2 万个独立环境。这个数说明 coding RL 需要大量能同时稳定运行的沙箱，Qwen 用这个量级来说明 coding agent 的环境成本，它算不上入门 threshold。

SkyRL 那边，NovaSky 的 SkyRL-v0（搭在 VeRL 和 OpenHands 上）和后续的 SkyRL-Agent 做的是异步多轮 rollout、通用工具和可扩展的环境执行，报告 throughput 约为朴素实现的 4 到 5 倍。它把环境服务和训练拆开部署。

面试里讲扩展，我会讲「环境副本数」和「每个副本的任务队列」，报实际能稳定跑的副本数和 hang 率，峰值并行数只作参考。只说「开了 GRPO」，听不出环境能不能撑住。

## 追问

**环境服务为什么要和训练分开部署？**
同机部署适合演示，规模一大就容易争用磁盘。SkyRL 把两者拆开，也是为了这个。

**SkyRL-Agent 比 v0 多做了什么？**
它把 dispatcher 和工具（包括 AST 搜索）写进了配方，还接入了 Prime Intellect Environments Hub 和 mini-SWE-agent。

**异步 rollout 带来的 off-policy 怎么办？**
记录环境版本和策略版本，过期 trajectories 降权或丢掉，见 `dt-onpolicy-pref`。

**环境能跑起来了，任务从哪来？**
造题的配方见 `dt-agent-tmax-synth`。
