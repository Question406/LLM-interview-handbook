---
id: dt-agent-passk-zero
section: posttrain-data
order: 25
level: S
title: Agent RL 一组 rollout 全零或全一对，这批任务还要不要？
quick: "组内全 0 或全 1，无法提供相对好坏的学习信号，可以丢掉或降权。优先训练当前模型偶尔能成功、仍有提升空间的任务；从未解出的先检查是否有问题，再决定搁置。模型更新后要重新估计 pass@$k$，不能永久固定难度分组。"
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

按 pass@$k$ 划分任务难度。采用组内相对优势时，全对或全错都没有奖励差异，因此优先保留当前模型偶尔能解、但多数时候还会失败的题。Agent rollout 成本高，一组 8 条全失败，就消耗了 8 份沙箱资源却没有组内对比信号。数学 基于可验证奖励的强化学习（RLVR） 已经把这件事写进配方，见 `dt-math-passk-band`。

常见误区是：从未被任何策略解出的题硬留在 强化学习（RL） 队列，或把一年前的「难题」冻住不重算。

公开配方里 2025-08 那篇多轮 SWE RL（DAPO）把组内优势为 0 的样本丢掉。第二阶段还剪两类：历次迭代成功率已经 $\ge 2/3$ 的（太容易），以及从未被解出的（很可能无解）。Qwen3-Coder 的大规模并行让你有预算去估 pass@$k$，预算仍应花在中间带。R1 一类配方对可验证任务同样依赖非退化的组内方差。TMax 造题时甚至跳过教师验题，把全零组交给这一刀，见 `dt-agent-tmax-synth`。

## 操作

对每个 `task_id` 记：当前策略 $k$ 次里成功几次、历史上是否有过成功、平均步数。

- 全 1：降权或移出，留给回归测试。
- 中间：进 RL 队列。
- 全 0 但曾经有人 / 教师解出：提示或工具可能坏了，查 harness。
- 全 0 且从未解出：搁置，等更强教师或更短 horizon 的子任务。

策略一升级，带要重算。冻结一年前的「难题」会变成今天的全 1。

和 τ-bench 的跨次不稳定区分：那边是同一任务多次跑抖，见 `dt-tau-passk`。这里是组内没有正负对比。抖的任务先当 flaky 扔掉，见 `dt-agent-rl-filter`，不要进中间带。

苹果：预算更紧，更要中间带。并行环境不是用来穷举不可解 issue 的。许可环境或验证合成里重算 pass@$k$；用户日志默认不进基础模型。

## 追问

- **教师能解、学生全 0，能不能蒸馏？** 能，我会走 监督微调（SFT） / 拒绝采样，先别 RL。RL 要学生自己摸到非零。
- **拆子任务？** 长 horizon 全 0 时，我会把「能跑测」和「能过测」切开，给过程检查点。过程奖励要防 hack，见 `dt-agent-reward-spec`。
- **苹果预算更紧？** 更要中间带。我不会用并行环境去穷举不可解 issue。
