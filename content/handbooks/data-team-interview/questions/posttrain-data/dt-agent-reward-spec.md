---
id: dt-agent-reward-spec
section: posttrain-data
order: 21
level: S
title: Agent RL 的奖励怎么写，怎样才不算被 hack？
quick: "奖励 $r$ 以隐藏测试或最终状态检查为准，可以是 0/1，也可以按测试点计分。可见测试的结果作为环境反馈，不作为最终奖励。补丁与标准补丁的文本相似度会压低功能等价但写法不同的解法，因此只能作辅助信号。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - RL
  - Reward
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-11
sources:
  - title: SWE-RL
    url: https://arxiv.org/abs/2502.18449
    type: primary
  - title: Training Long-Context, Multi-Turn Software Engineering Agents with Reinforcement Learning
    url: https://arxiv.org/abs/2508.03501
    type: primary
  - title: "Will Brown: RL Environments at Scale"
    url: https://ai.engineer/talks/rl-environments-at-scale
    type: secondary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先区分模型能读到的反馈和用于评分的检查。训练时可以把公开测试、复现测试的 stdout 给模型看；奖励则只根据隐藏测试或状态断言计算。这是 RLEF 拆法的代码版，见 `dt-rlef-split`、`dt-code-hidden-tests`。

不这么选的理由：SWE-RL 用 `SequenceMatcher` 打预测 patch 和 oracle patch，格式错给 $-1$。这种评分可以离线扩展，但更鼓励补丁接近某次实际合入的写法；功能正确、写法不同的补丁可能被压低分。后来那篇多轮 SWE 强化学习（RL） 改成测试 0/1 加长度惩罚，方向才对。

## 我会怎么防 hack

常见捷径：改测试文件、删断言、把输入写进哈希表。成功轨迹里改了测试文件，整段当负例，见 `dt-swe-success-noise`。网页 / GUI 漏金补丁、漏 URL，见 `dt-webarena-traj`。

Rubric 可以拆开：隐藏测权重 1，格式分很小，日志项权重 0 只盯 hack。奖励上涨而产品行为变差，说明代理指标可能没有约束住实际目标。长度惩罚防刷步数。不要把「想得长」写进 $r$。

神经奖励模型（RM）可以在补丁通过测试后评价风格，使用前需要校准。主要正确性检查仍应依赖执行。

苹果：许可仓库或合成环境里的隐藏测。用户会话默认不进基础模型，也不能拿用户「看起来修好了」当 $r$。

## 追问

- **oracle 相似度完全不能用？** 当辅助特征可以。和隐藏测打架时听测。
- **没有隐藏测的桌面任务？** 终局状态检查器，检查脚本放只读镜像，agent 工作区碰不到。
- **人看一眼当奖励？** 太慢。人工适合抽查钻奖励漏洞的样本、修订评分标准，不适合给每次训练尝试实时评分。
