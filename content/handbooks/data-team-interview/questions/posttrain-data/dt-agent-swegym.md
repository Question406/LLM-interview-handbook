---
id: dt-agent-swegym
section: posttrain-data
order: 14
level: S
title: SWE-Gym：用可执行仓库当数据工厂，轨迹怎么留、verifier 怎么训？
quick: "SWE-Gym 把真实 Python 任务、可执行环境和单测作为训练工厂。采样后，用独立测试筛成功轨迹做 SFT，再用成败训练 outcome verifier。任务池与评测隔离，并检查改测试、漏回归和环境版本；通过测试是必要条件，但还不是充分条件。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - Coding
  - SWE
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: SWE-Gym
    url: https://arxiv.org/abs/2412.21139
    type: primary
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

可执行仓库提供任务环境，当前策略在其中采样，grader 用测试判断成败。成功轨迹可用于 SFT，成功与失败轨迹一起用于训练结果验证器（outcome verifier），推理时再给多条候选轨迹评分。公开锚点是 SWE-Gym：2438 个真实 Python 任务，带可执行环境和单测，SWE-bench Verified / Lite 涨了；再用成败轨迹训 verifier，resolve 再涨。

常见误区是：没有可跑的测试，SWE 数据回到看 diff 像不像。过测是必要，不是充分；成功轨迹仍要挡改测试、漏回归，见 `dt-swe-success-noise`。

## 工厂流程

1. 任务池和门禁切开。Gym 训练任务 $\ne$ SWE-bench test。
2. 当前策略采样 $k$ 条轨迹。
3. 隐藏测打标签。
4. 成功且过程可重放的轨迹进入 SFT；失败轨迹可用于 RM、偏好或 verifier 训练。
5. 更新策略，任务难度带要重扫，见 `dt-math-passk-band`。

这里的 verifier 学习最终结果，不逐步给 PRM 标签。软件工程步骤很难逐一标对错，最终测试相对便宜。但仍要抽查 diff，防止乱改代码后碰巧通过测试的轨迹被当作可靠过程。

## 环境资产

将 Docker、依赖和测试哈希写入数据血缘。环境变化可能让昨天通过的轨迹今天无法运行，造成数据连锁问题（cascade），见 `dt-data-cascade`。这比网页过滤更脆。

苹果：许可仓库或验证合成，grader 仍要真测试。用户仓库默认不进基础模型。仓库 agent 是 server 侧；端侧留函数级补全桶，见 `dt-code-repo-vs-fn`。

## 追问

- **合成仓库行不行？** 当种子可以，grader 仍要真测试。LLM 写的假项目加假测试，是 HumanEval 自嗨的放大。我不会当门禁。
- **非 Python？** 同一合同，环境按语言复制。没有可执行器就不要称 SWE 数据。
- **端侧？** 仓库 agent 是 server 侧。端侧我会留函数级补全桶。
