---
id: dt-agent-rl-filter
section: posttrain-data
order: 20
level: S
title: 2 万条 SWE 任务，怎么滤成能拿来做 Agent RL 的集合？
quick: "先做四项静态检查：任务是否有效、复杂度是否合适、LLM 质量标签是否过关、测试是否稳定。SWE-rebench 的原始任务不能直接用于 Agent RL，公开做法从 21336 条滤到 7249。进入训练后，再移除当前模型始终失败或太容易的任务，目标是留下可学习、可复现的任务。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - SWE
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Training Long-Context, Multi-Turn Software Engineering Agents with Reinforcement Learning
    url: https://arxiv.org/abs/2508.03501
    type: primary
  - title: SWE-rebench
    url: https://arxiv.org/abs/2505.20411
    type: primary
  - title: Introducing SWE-bench Verified
    url: https://openai.com/index/introducing-swe-bench-verified/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先过滤任务，再训练。SWE-rebench 从约 3400 个 Python 仓库自动收集了可执行任务，但原始数据不能直接拿去做 GRPO。我会做四项静态检查：任务是否有效、复杂度是否合适、质量分是否过关、测试是否稳定。

## 为什么不能直接训

2 万条任务看起来都像 issue，但其中有的需要步骤太多，有的说明依赖没给出的内部名称，有的测试结果不稳定。这些任务进了分组训练，组内奖励差异主要来自噪声，反映不了不同尝试的真实好坏。公开做法（2025-08 那篇长上下文多轮 SWE 强化学习（RL），Qwen2.5-72B，DAPO）从 21336 条滤到了 7249 条。

## 训练前的四项检查

**正确性。** 元数据里测试失败原因是 `AttributeError`、`ImportError` 这类无效引用的，直接扔掉。这种任务 agent 没有足够信息，只能去猜内部名称。OpenAI 在 Verified 里标的 underspecified 是同一类问题，不过他们用人审。

**复杂度。** 只保留最多改 7 个文件、少于 500 行的任务。完成任务需要的步骤太多时，稀疏奖励很难归因到具体动作上。

**LLM 质量分。** SWE-rebench 的元数据里有教师模型打的质量分。标成 3.0 的丢掉，它们通常说明不清、过于复杂，或测试补丁有问题。这相当于自动版的 Verified：Verified 靠人审 500 条，这里靠教师模型打分。

**确定性。** 同一环境把测试跑 50 次，结果抖动的当 flaky。外部服务、时间、浮点是常见来源。测试不稳定会让奖励波动，组内方差就反映不了不同尝试的真实效果。50 次听起来贵，但只需在训练前离线做一次，结果写进元数据，训练过程中不用每次重测。

当前模型全失败或几乎全成功的任务，不在这四项静态检查里，要等进入 RL 后再处理，见 `dt-agent-passk-zero`。

评测和训练也要分开：评测用 SWE-bench Verified，训练用 rebench，并按月切 holdout（文中 May-June 的任务不进训练）。按时间切是代码评测门禁的标配，参考 LiveCodeBench 和 `dt-code-bench-bleed`。

手里没有 GitHub issue 池时，流程也一样：用许可仓库或合成仓库，照样跑 fail-to-pass 和确定性检查，数据来源的许可见 `dt-license-is-quality`。

## 滤完要留下的字段

`task_id`、环境镜像哈希、fail-to-pass 测试名、flaky 试验次数、是否曾被解出、说明字数。四项检查的阈值写进 datasheet。没有这些，下周就无法复现这次过滤。

## 追问

- **自动再收一批，还要滤吗？** 更要滤。规模越大，flaky 任务和说明不清的垃圾任务占比越高。
