---
id: dt-zero-advantage-groups
section: panel
order: 45
level: A
title: Panel 情景：组内奖励几乎都一样，RL 数据怎样恢复学习信号？
quick: 假设同一道题采了 8 个回答，全部奖励为零。减去组均值后仍全是零，没有哪个回答相对更好；全部奖励为一时也一样。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 情景练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
---

## 题目描述

原创 post-training 情景，建议 35 分钟。每个 prompt 采 8 条回答，以组内中心化奖励训练。75% 的组内奖励完全相同，其中大部分全错，少数全对。训练 loss 在变化，能力分数却几乎不动。团队建议直接将 sampling 数从 8 提到 64。

请排查“奖励相同”的原因，提出数据与训练实验，解释为什么 loss 变化也不能证明任务学习发生。数字是练习约定。

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

## 解题思路与参考答案

同一组奖励都相等时，减去组均值或其他成员均值后的任务优势为零。仍可能有 KL、熵项或其他监督项推动参数，所以 loss 变化不代表从任务奖励中学到了能力。

### 先检查奖励是否可信

抽查超时、解析失败、executor 错误是否统一被写成零，检查正负控制样本是否得到预期奖励。全错可能是任务超出当前模型能力，也可能是环境坏了；全对可能太容易，也可能 verifier 放水。按终止原因和 verifier 版本 evaluation slices，不能只看平均奖励。

### 数据与 sampling 干预

对可信任务，用 current policy 测首答和多次 sampling 成功率，选择有一定概率解对的中间难度任务，保留容易与困难任务作覆盖对照。检查组内答案是否 near-duplicates；适当调整生成多样性、任务表述或搜索路径，同时核验是否只是制造更长无效答案。若能得到可靠的阶段状态或形式验证，可以补充分步信号；不能用不可靠 judge 给全错答案强行排个高低。

### 如何比较 8 与 64

在相同总生成与执行预算下，对比“少量任务每题采 64”与“更多任务每题采 8”，观察有效优势组比例、独立任务覆盖、gradient 方差与最终迁移。若错误是固定的知识或工具 schema 缺口，多采 8 倍可能仍全错。必要时先用经过验证的示范做 SFT，再重新测任务可学区间。

## 面试追问

**是否永久丢掉全错组？** 不宜永久丢弃；模型改变后难度会变，且可能把重要风险类别全部过滤掉。记录原因并定期重测。

**只留有不同奖励的组会怎样？** 会改变目标分布，应报告保留率和被排除任务，必要时结合独立监督与覆盖评测。

**为什么不把正确答案直接给进去？** 可以生成示范数据，但这改变了训练目标与预算，应作为明确对照，而不是假装仍是纯组 sampling RL。
