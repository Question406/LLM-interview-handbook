---
id: dt-agent-passk-zero
section: posttrain-data
order: 25
level: S
title: Agent RL 一组 rollout 全零或全一对，这批任务还要不要？
quick: 假设同一道题采了 8 个回答，全部奖励为零。减去组均值后仍全是零，没有哪个回答相对更好；全部奖励为一时也一样。
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Difficulty
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: >-
      Training Long-Context, Multi-Turn Software Engineering Agents with
      Reinforcement Learning
    url: 'https://arxiv.org/abs/2508.03501'
    type: primary
  - title: Qwen3-Coder
    url: 'https://qwenlm.github.io/blog/qwen3-coder/'
    type: primary
  - title: DeepSeek-R1
    url: 'https://arxiv.org/abs/2501.12948'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 回答思路

> **问题与场景：** 假设同一道题采了 8 个回答，全部奖励为零。
>
> **做法与原因：** 标准差为零需要数值处理，但加一个 epsilon 只能防止除零，不能制造学习信号。
>
> **检查与取舍：** 我会统计全平组比例、每题通过率和独立评估。

## 可以这样回答

假设同一道题采了 8 个回答，全部奖励为零。减去组均值后仍全是零，没有哪个回答相对更好；全部奖励为一时也一样。

标准差为零需要数值处理，但加一个 epsilon 只能防止除零，不能制造学习信号。应检查题是否太难、太简单，或者 verifier 没有区分度，再调整课程、sampling 或任务。

我会统计全平组比例、每题通过率和独立评估。简单丢掉所有困难题可能让覆盖变差，因此还要保留让困难任务产生正负对照的办法。

## 技术备查

这批任务大多不该留在 RL 队列里。按组内相对优势训练时，一组全对或全错就没有奖励差异，gradient 为零。所以要按 pass@$k$ 给任务分难度，优先留当前模型偶尔能解、多数时候还会失败的题。

Agent rollout 很贵，这笔账比数学题更值得算。一组 8 条全失败，就烧掉了 8 份沙箱资源，却拿不到任何组内对比信号。数学方向的基于 verifiable reward 的 RL（RLVR）早就把这件事写进了配方（见 `dt-math-passk-band`），2025-08 那篇多轮 SWE RL（DAPO）也直接丢掉组内优势为 0 的样本。

具体做法是对每个 `task_id` 记三样东西：current policy $k$ 次里成功几次、历史上有没有成功过、平均步数。全 1 的降权或移出，留作 regression tests；中间的进 RL 队列。全 0 的要分开看：以前有策略或 teacher 解出过的，多半是提示或工具坏了，先查 harness；从来没解出过的先搁置，等更强的 teacher，或者拆成 horizon 更短的子任务。

策略一升级，difficulty band 就要重算。一年前标定的「难题」，今天可能已经是全 1 了。常见的两个错误就是把这种标定冻住不再重算，以及把从来没有任何策略解出过的题硬留在队列里。

还有一类情况要和这里分开。τ-bench 说的是同一任务多次运行结果抖动（见 `dt-tau-passk`），这里说的是组内没有正负对比。结果抖动的任务先当 flaky 扔掉（见 `dt-agent-rl-filter`），免得它混进中间带。

## 追问

**公开配方具体剪了哪些题？**
2025-08 那篇多轮 SWE RL 在第二阶段剪两类：历次迭代成功率已经 $\ge 2/3$ 的（太容易），和从未被解出的（很可能无解）。Qwen3-Coder 的大规模并行让人有预算去估 pass@$k$，但预算还是应该花在中间带；R1 一类配方对可验证任务同样依赖组内方差不退化。

**造题时要不要先让 teacher 验一遍？**
不一定。TMax 造题时就跳过了 teacher 验题，把全零组留到训练这一步来剪，见 `dt-agent-tmax-synth`。

**teacher 能解、student 全 0，能不能 distillation？**
能。我会先走 SFT 或 rejection sampling，暂时不上 RL，因为 RL 要等 student 自己能摸到非零奖励。

**长 horizon 任务全 0，能拆子任务吗？**
可以。我会把「能跑通测试」和「能通过测试」分开，给过程检查点。process reward 要防 hack，见 `dt-agent-reward-spec`。
