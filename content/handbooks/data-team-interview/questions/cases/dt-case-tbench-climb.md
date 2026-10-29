---
id: dt-case-tbench-climb
section: cases
order: 6
level: S
title: 研究案例：想在 Terminal-Bench 上爬坡，RL 环境数据怎么做？
quick: >-
  几篇公开工作放在一起看，结论是环境要贴近真实任务、难度卡在中间、verifier 靠得住，环境数量排在最后。Endless Terminals 在自己的
  development set 上涨了很多，到 Terminal-Bench 几乎不动；River 只用不到三成的环境，过滤掉坏 verifier
  后增益更大。
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Synthetic Data
  - Data Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: >-
      Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command
      Line Interfaces
    url: 'https://arxiv.org/abs/2601.11868'
    type: primary
  - title: 'Endless Terminals: Scaling RL Environments for Terminal Agents'
    url: 'https://arxiv.org/abs/2601.16443'
    type: primary
  - title: 'TMax: A simple recipe for terminal agents'
    url: 'https://arxiv.org/abs/2606.23321'
    type: primary
  - title: 'Lambert: TMax, an open RL recipe for terminal agents'
    url: 'https://natolambert.substack.com/p/tmax-an-open-rl-recipe-for-terminal'
    type: secondary
  - title: Learning Generalizable Behaviors for Terminal Agents (River)
    url: 'https://arxiv.org/abs/2608.22631'
    type: primary
  - title: >-
      Terminal-Universe: Turning Agent Trajectories into Scalable Terminal
      Environments
    url: 'https://arxiv.org/abs/2609.04148'
    type: primary
---

简单说，这几篇放在一起看，结论是：环境要贴近真实任务，难度卡在中间，verifier 要靠得住，环境数量排在最后。

先看目标。Terminal-Bench 2.0 一共 89 题，每题一个 Docker 环境，测试只看容器最后的状态，不管 agent 中间敲了什么。题目从编译 Linux 到逆向二进制都有，前沿模型也做不到 65%。

Endless Terminals 是个很好的反面例子。他们全自动生成了三千多个终端任务，Qwen2.5-7B 在自己的 development set 上从 10.7% 训到 53.3%，到 Terminal-Bench 2.0 只从 2.2% 涨到 3.4%。他们的任务基本是文件操作、日志处理这一类，比真实分布窄得多，也简单得多。

TMax 就是冲着这个问题改的：按领域、技能、复杂度这些维度组合出题，造了一万四千多个环境，同一个 teacher 在上面 pass@1 大约四成，难度刚好。9B 模型训完到了 27%。

River 又往前走了一步。它只用了不到三成的 TMax 环境，把 verifier 质量差的过滤掉，RL 的增益比用全部环境还大。坏的 verifier 会奖励错误的行为，环境越多，这种错误越多。

Terminal-Universe 换了一个来源：拿公开的 agent trajectories，replay 里面的文件操作，把 agent 当时的工作区还原出来，再在上面出题，一共三万七千多个环境，光做 SFT 就涨了 11.9 分。真实 trajectories 自带真实的任务分布，这恰好是合成 pipeline 最难模仿的地方。

如果让我来做，我会先把 verifier 定下来：每个环境用参考解跑一遍必须通过，什么都不做必须失败。来源上，合成环境和真实 trajectories 还原的环境混着用，分开统计各自的贡献。训练中按当前模型的 pass@k 把全对和全错的题剪掉。最后对 Terminal-Bench decontamination，internal held-out evaluation set 用自己的私有集。

## 追问

**数量和质量只能保一个，保哪个？**
先保质量。坏 verifier 会直接奖励错误行为，River 用三成的环境就赢了全量。

**TMax 为什么不要求 teacher 先解出来才留题？**
RL 训练时全零的组本来就会被丢掉，生成阶段只要保证镜像能 build，省成本。代价是 verifier 可能偏弱，要抽查。具体配方见 `dt-agent-tmax-synth`。

**SFT 和 RL 分别用什么数据？**
真实 trajectories 适合拿来做 SFT 打底；RL 需要能反复交互、判分稳定的环境，合成环境加上 verifier 过滤更合适。

**怎么确认不是刷了某个 harness？**
换几个 agent harness 再测。TMax 换了 harness 增益还在；只在一个 harness 上涨，可能只是学会了它的格式。

相关：`dt-agent-env-is-data`、`dt-agent-passk-zero`、`dt-agent-scale-env`、`dt-bench-vs-user`、`dt-frontier-agent-sets`
