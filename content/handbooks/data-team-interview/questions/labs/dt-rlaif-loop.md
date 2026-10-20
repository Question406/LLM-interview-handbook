---
id: dt-rlaif-loop
section: labs
order: 9
level: A
title: Anthropic：RLAIF / 宪法反馈，judge 开始喜欢自己的文风怎么办？
quick: "固定 judge 的版本，避免每轮都换成正在训练的生成器；用人工和规则独立检查结果。能直接验证的任务优先用规则奖励，存在明显人评分歧的题不要全交给 RLAIF。苹果场景还要确认 judge 所需的数据来源，不能默认读取用户原文。"
companies:
  - apple
tags:
  - Anthropic
  - RLAIF
  - Preference
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Constitutional AI
    url: https://arxiv.org/abs/2212.08073
    type: primary
  - title: "RLAIF vs. RLHF (Lee et al.)"
    url: https://arxiv.org/abs/2309.00267
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

固定 judge 的版本，不要每轮都把它换成当前策略模型。评价原则写清楚：回答要简短、有证据，不能靠客套堆砌得分。用人评检查和 cohesion 选择 prompt；AFM 中有 20-30% 的题存在人评分歧，不宜直接交给 RLAIF。能明确验证的任务用规则奖励。judge 可以在适合的任务上减少人工标注，但最终检查仍需要人和规则。

Constitutional AI 减少人工标注，不代表标签自动更可靠。策略模型可能越来越会模仿 judge 的长文和套话；judge 给高分，下一轮便继续强化这种文风，人评却没有进步，甚至下降。要像 `dt-judge-bias`、`dt-length-hack-data` 中一样，检查回答长度、judge 对同家族模型的偏好，以及与人评的一致性 kappa。

接到苹果：AFM 公开是人偏好训 奖励模型（RM），加规则奖励，不是 CAI。在苹果场景中，还要检查 judge 是否需要读取用户原文；不能默认这类训练数据通道存在。把原则写进系统提示，是推理时的要求。训练数据仍要展示怎样遵守这些原则，仅靠约束解码无法保证内容符合要求。和 Self-Rewarding 的差别：宪法至少有外置原则，Self-Rewarding 连原则也是自己写，见 `dt-self-improve`。

公开锚点：CAI 先用原则做批评和改写，再让模型按原则标偏好；RLAIF vs 基于人类反馈的强化学习（RLHF） 论文报过接近的效果。

## 追问

- **原则写进系统提示算不算数据？** 推理时约束。训练数据仍要示范这些原则，否则约束解码管不了内容。
- **和 Self-Rewarding 的差别？** 宪法至少有外置原则。Self-Rewarding 连原则也是自己写，见 `dt-self-improve`。
