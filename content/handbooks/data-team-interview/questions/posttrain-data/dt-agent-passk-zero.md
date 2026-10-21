---
id: dt-agent-passk-zero
section: posttrain-data
order: 25
level: S
title: Agent RL 一组 rollout 全零或全一对，这批任务还要不要？
quick: "全 0 或全 1 的组没有相对好坏，组内优势为零，可以丢掉或降权。预算优先给当前模型偶尔能成功、多数时候还失败的中间带任务；从未解出的先查环境是否坏了，再决定搁置。策略更新后要重算 pass@$k$，难度分组不能一直冻结。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Difficulty
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Training Long-Context, Multi-Turn Software Engineering Agents with Reinforcement Learning
    url: https://arxiv.org/abs/2508.03501
    type: primary
  - title: Qwen3-Coder
    url: https://qwenlm.github.io/blog/qwen3-coder/
    type: primary
  - title: DeepSeek-R1
    url: https://arxiv.org/abs/2501.12948
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

这批任务大多不该留在 RL 队列里。用组内相对优势训练时，一组全对或全错就没有奖励差异，梯度为零。所以按 pass@$k$ 给任务分难度，优先保留当前模型偶尔能解、但多数时候还会失败的题。

## 为什么要剪

Agent rollout 很贵。一组 8 条全失败，就烧掉了 8 份沙箱资源，却没有组内对比信号。数学方向的基于可验证奖励的强化学习（RLVR）已经把这件事写进了配方，见 `dt-math-passk-band`。

公开配方也是这么做的。2025-08 那篇多轮 SWE RL（DAPO）直接丢掉组内优势为 0 的样本；第二阶段再剪两类任务：历次迭代成功率已经 $\ge 2/3$ 的（太容易），以及从未被解出的（很可能无解）。Qwen3-Coder 的大规模并行让人有预算去估 pass@$k$，但预算仍然应该花在中间带。R1 一类配方对可验证任务同样依赖组内方差不退化。TMax 造题时甚至跳过教师验题，把全零组留给这一步来剪，见 `dt-agent-tmax-synth`。

常见的两个错误：把从来没有任何策略解出过的题硬留在强化学习（RL）队列里；或者把一年前标定的「难题」冻住，不再重算。

## 怎么操作

对每个 `task_id` 记录三样东西：当前策略 $k$ 次里成功几次、历史上是否有过成功、平均步数。然后按结果分流：

- 全 1：降权或移出，留作回归测试。
- 中间：进 RL 队列。
- 全 0，但以前有策略或教师解出过：多半是提示或工具坏了，先查 harness。
- 全 0 且从未解出：搁置，等更强的教师，或者拆成 horizon 更短的子任务。

策略一升级，难度带就要重算。一年前冻结的「难题」，今天可能已经是全 1。

还要和 τ-bench 的跨次不稳定区分开。那里说的是同一任务多次运行结果抖动（见 `dt-tau-passk`），这里说的是组内没有正负对比。结果抖动的任务先当 flaky 扔掉（见 `dt-agent-rl-filter`），免得它混进中间带。

## 追问

- **教师能解、学生全 0，能不能蒸馏？** 能。我会先走监督微调（SFT）或拒绝采样，暂时不上 RL，因为 RL 要等学生自己能摸到非零奖励。
- **长 horizon 任务全 0，能拆子任务吗？** 可以。我会把「能跑通测试」和「能通过测试」分开，给过程检查点。过程奖励要防 hack，见 `dt-agent-reward-spec`。
