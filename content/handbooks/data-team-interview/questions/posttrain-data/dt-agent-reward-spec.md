---
id: dt-agent-reward-spec
section: posttrain-data
order: 21
level: S
title: Agent RL 的奖励怎么写，怎样才不算被 hack？
quick: "奖励 $r$ 以隐藏测试或最终状态检查为准，可以是 0/1，也可以按测试点计分。可见测试的结果只作为环境反馈给模型看，不进最终奖励。补丁与标准补丁的文本相似度会压低功能等价但写法不同的解，只能当辅助信号。"
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

奖励 $r$ 只根据隐藏测试或最终状态断言计算，可以是 0/1，也可以按测试点计分。关键是先分清两类东西：模型能读到的反馈，和用来打分的检查。训练时可以把公开测试、复现测试的 stdout 给模型看，但这些不进 $r$。这是 RLEF 那种拆法在代码任务上的版本，见 `dt-rlef-split`、`dt-code-hidden-tests`。

## 为什么不用 patch 相似度

SWE-RL 用 `SequenceMatcher` 比较预测 patch 和 oracle patch 打分，格式错给 $-1$。这种评分不用跑环境，离线就能扩展，但它奖励的是「写得像某次实际合入的补丁」：功能正确、写法不同的补丁可能被压低分数。后来那篇多轮 SWE 强化学习（RL）改成测试 0/1 加长度惩罚，方向才对。oracle 相似度可以留作辅助特征，和隐藏测试冲突时以测试为准。

## 怎么防 hack

以执行结果为奖励，模型就会找执行层面的捷径：改测试文件、删断言、把测试输入写进哈希表。成功轨迹里如果改了测试文件，整段当负例处理，见 `dt-swe-success-noise`。网页和 GUI 任务里则要防金补丁、目标 URL 泄漏给 agent，见 `dt-webarena-traj`。

Rubric 可以拆成几项：隐藏测试权重 1，格式分很小，日志项权重 0、只用来盯 hack。加长度惩罚防止刷步数，但不要把「想得长」写进 $r$。如果奖励在涨、产品行为却在变差，说明代理指标没有约束住实际目标。

神经奖励模型（RM）可以在补丁通过测试之后评价风格，用之前要校准。正确性检查仍然要靠执行。

## 追问

- **没有隐藏测试的桌面任务怎么办？** 写终局状态检查器。检查脚本放在只读镜像里，agent 的工作区碰不到。
- **让人看一眼当奖励行不行？** 太慢。人工适合抽查那些钻奖励漏洞的样本、修订评分标准，不适合给每次训练尝试实时打分。
