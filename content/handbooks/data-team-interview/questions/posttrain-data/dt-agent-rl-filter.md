---
id: dt-agent-rl-filter
section: posttrain-data
order: 20
level: S
title: 2 万条 SWE 任务，怎么滤成能拿来做 Agent RL 的集合？
quick: >-
  先做四项静态检查：任务是否有效、复杂度是否合适、LLM 质量标签是否过关、测试是否稳定。SWE-rebench 的原始任务不能直接拿去做 Agent
  RL，公开做法从 21336 条滤到 7249 条。进入训练后，再移除当前模型始终失败或太容易的任务，留下能学、能复现的部分。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: >-
      Training Long-Context, Multi-Turn Software Engineering Agents with
      Reinforcement Learning
    url: 'https://arxiv.org/abs/2508.03501'
    type: primary
  - title: SWE-rebench
    url: 'https://arxiv.org/abs/2505.20411'
    type: primary
  - title: Introducing SWE-bench Verified
    url: 'https://openai.com/index/introducing-swe-bench-verified/'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先过滤再训练。SWE-rebench 从约 3400 个 Python 仓库自动收集了可执行任务，原始数据不能直接拿去做 GRPO。我会做四项静态检查：任务是否有效、复杂度是否合适、质量分是否过关、测试是否稳定。2025-08 那篇 long context 多轮 SWE RL（Qwen2.5-72B，DAPO）就是这样从 21336 条滤到了 7249 条。

2 万条任务看起来都像 issue，里面却混着各种毛病。比如一条任务的测试报 `AttributeError`，因为它引用了一个说明里没给出的内部名称，agent 拿不到足够信息，只能去猜。还有的需要步骤太多，有的测试结果不稳定。这些任务进了分组训练，组内奖励差异主要来自噪声，反映不了不同尝试的真实好坏。

四项检查我按这个顺序做。先查正确性，元数据里测试失败原因是 `AttributeError`、`ImportError` 这类无效引用的直接扔掉。再查复杂度，只保留最多改 7 个文件、少于 500 行的任务，步骤太多时稀疏奖励很难 attribution 到具体动作上。然后看 LLM 质量分，SWE-rebench 元数据里有 teacher model 打的质量分，标成 3.0 的丢掉，它们通常说明不清、过于复杂，或者测试补丁有问题。

最后查确定性。同一环境把测试跑 50 次，结果抖动的当 flaky，常见来源是外部服务、时间和浮点。测试不稳定，奖励就跟着波动，组内方差反映不了不同尝试的真实效果。50 次听起来贵，但只在训练前离线做一次，结果写进元数据，训练过程中不用每次重测。

当前模型全失败或几乎全成功的任务不在这四项静态检查里，要等进了 RL 再处理（见 `dt-agent-passk-zero`）。

滤完我会留下这些字段：`task_id`、环境镜像哈希、fail-to-pass 测试名、flaky 试验次数、是否曾被解出、说明字数，四项检查的阈值写进 datasheet。没有这些，下周就没法复现这次过滤。

## 追问

**质量分这一步和 SWE-bench Verified 有什么关系？**
可以看成自动版的 Verified。OpenAI 在 Verified 里标的 underspecified 是同一类问题，Verified 靠人审 500 条，这里靠 teacher model 打分。

**training set 和 evaluation set 怎么分？**
评测用 SWE-bench Verified，训练用 rebench，并按月切 holdout（文中 May-June 的任务不进训练）。按时间切是代码 evaluation gate 的标配，参考 LiveCodeBench 和 `dt-code-bench-bleed`。

**手里没有 GitHub issue 池怎么办？**
流程一样。用许可仓库或合成仓库，照样跑 fail-to-pass 和确定性检查，数据来源的许可见 `dt-license-is-quality`。

**自动再收一批，还要滤吗？**
更要滤。规模越大，flaky 任务和说明不清的垃圾任务占比越高。
