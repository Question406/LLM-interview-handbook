---
id: dt-agent-scale-env
section: posttrain-data
order: 23
level: S
title: Agent RL 怎么把环境扩到能真正跑起来？Qwen 和 SkyRL 各做了什么？
quick: "先让单个任务在干净容器里稳定复现，再增加并行环境。Qwen 同时运行 2 万个独立环境；SkyRL 用异步执行、任务调度和工具服务提高吞吐。扩规模时先检查超时、依赖和文件系统隔离，不能只换 RL 算法。"
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

先说明能稳定运行多少环境、挂起比例多高，再谈 PPO。并行环境数、每条轨迹的长度，以及怎样隔离失败，都比算法细节更需要先解决。Qwen 博客把瓶颈写成 environment scaling，不是又换一个 强化学习（RL） 算法。造题配方见 `dt-agent-tmax-synth`。

常见误区是：单环境还复现不了，直接喊 2 万并行。环境死掉、依赖互串、磁盘打满，采样轨迹（rollout） 就变成噪声。

## 两家公开锚点

Qwen3-Coder。后训练上了 long-horizon Agent RL：多轮规划、调工具、看反馈。他们借助阿里云同时跑 2 万个独立环境。这个数字说明，coding RL 需要大量能同时稳定运行的沙箱。

SkyRL。NovaSky 的 SkyRL-v0（搭在 VeRL / OpenHands 上）和后续 SkyRL-Agent：异步多轮 rollout，通用工具，可扩展的环境执行。他们报相对朴素实现约 4 到 5 倍吞吐。SkyRL-Agent 再把 dispatcher 和工具（含 AST 搜索）写进配方，还接了 Prime Intellect Environments Hub 和 mini-SWE-agent。现场说「环境副本数」和「每副本任务队列」，不要只说「开了 GRPO」。

## 扩之前的清单

单任务能否在干净容器里复现；超时和 OOM 是否记成明确失败而不是挂起；并行时文件系统 / 端口 / 缓存是否隔离；失败环境是否污染邻居。这些检查不通过时，增加到 2 万并行，也只是同时运行大量不稳定的环境。

苹果：许可仓库在隔离执行环境里跑。产品用户会话不是并行环境池，用户日志默认不进基础模型。

## 追问

- **2 万是不是必须？** 不是门槛。我会报实际能稳定跑的副本数，以及 hang 率。Qwen 用这个量级说明 coding agent 的环境成本。
- **环境服务和训练同机？** 我会拆开，跟 SkyRL 同一方向。同机适合演示，扩大规模时却容易争用磁盘资源。
- **异步 rollout 的 off-policy 怎么办？** 我会记环境版本和策略版本。过期轨迹降权或丢掉，见 `dt-onpolicy-pref`。
