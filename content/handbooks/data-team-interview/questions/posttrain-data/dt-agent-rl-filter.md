---
id: dt-agent-rl-filter
section: posttrain-data
order: 20
level: S
title: 2 万条 SWE 任务，怎么滤成能拿来做 Agent RL 的集合？
quick: "先检查任务是否有效、复杂度是否合适、LLM 质量标签是否可靠，以及测试是否稳定。SWE-rebench 的原始任务不能直接用于 Agent RL；进入训练后，再移除当前模型始终失败或太容易的任务。关键是留下可学习、可复现的任务。"
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

先过滤任务，再训练。SWE-rebench 从约 3400 个 Python 仓库自动收集可执行任务，但原始数据不能直接用于 GRPO。

不能因为 2 万条任务看起来都像 issue，就直接分组训练。任务需要的步骤太多、说明依赖未给出的内部名称，或测试结果不稳定时，组内奖励差异可能主要来自噪声。公开做法（2025-08 那篇长上下文多轮 SWE 强化学习（RL），Qwen2.5-72B，DAPO）从 21336 条滤到 7249。

## 训练前的四项检查

正确性。元数据里测失败是 `AttributeError` / `ImportError` 这类无效引用的，扔掉。agent 没有足够信息，只能猜内部名称。OpenAI Verified 的 underspecified 是同一类，他们用人审。

复杂度。只留最多改 7 个文件、少于 500 行的。完成任务所需步骤太多时，很难把稀疏奖励归因到具体动作。

LLM 质量分。SWE-rebench 元数据里有教师打的质量分。丢掉标成 3.0 的：说明不清、过复杂、测试补丁有问题。这是自动版 Verified，不是人审 500 条。

确定性。同一环境跑 50 次测试，结果抖的当 flaky。外部服务、时间、浮点是常见源。测试不稳定会让奖励波动，组内方差便难以反映不同尝试的真实效果。

当前模型全失败或几乎全成功的任务，不属于这四项静态检查；进入 RL 后再处理，见 `dt-agent-passk-zero`。

评测用 SWE-bench Verified，训练用 rebench 且按月切 holdout（文中 May-June 不进训练）。时间切是代码门禁的标配，见 LiveCodeBench / `dt-code-bench-bleed`。

## 滤完要留下的字段

`task_id`、环境镜像哈希、fail-to-pass 测试名、flaky 试验次数、是否曾被解出、说明字数。没有这些，下周无法复现过滤。

苹果：没有 GitHub issue 池也一样。许可仓库或合成仓库，同样跑 fail-to-pass 和确定性。通道见 `dt-license-is-quality`。用户工单默认不进基础模型。

## 追问

- **50 次会不会太贵？** 我会训练前离线做一次，结果进元数据。训练过程中不要每次都重复测试 50 次。
- **自动再收一批还要滤吗？** 更要。规模越大，flaky 和说明垃圾占比越高。四刀的阈值写进 datasheet，下周才能复现。
- **苹果没有 GitHub issue 池？** 合同不变：许可仓库或合成仓库，同样跑 fail-to-pass 和确定性。
