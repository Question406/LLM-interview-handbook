---
id: dt-rlaif-loop
section: labs
order: 9
level: A
title: Anthropic：RLAIF / 宪法反馈，judge 开始喜欢自己的文风怎么办？
quick: "固定 judge 的版本，并用人评和规则独立检查结果。策略会越来越会模仿 judge 偏爱的长文和套话，judge 每轮换成当前策略，就等于让模型给自己打分，最后 judge 给高分、人评却不涨。能直接验证的任务优先用规则奖励，人评分歧明显的题留给人来判断。"
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

先固定 judge 的版本，不随策略模型一起更新，再用人评和规则独立检查结果。judge 可以在合适的任务上减少人工标注，最终把关仍要靠人和规则。

## 为什么会出问题

Constitutional AI 减少了人工标注，标签可不可靠仍要单独验证。CAI 的流程是先按原则让模型批评并改写，再让模型按原则标偏好；RLAIF 和基于人类反馈的强化学习（RLHF）的对比论文报过两者效果接近。但在循环里，策略模型会越来越会模仿 judge 喜欢的长文和套话：judge 给高分，下一轮继续强化这种文风，人评却没有进步，甚至下降。

## 怎么防

1. **固定 judge 版本。** 每轮换成当前策略，就等于让模型给自己打分。
2. **写清评价原则。** 回答要简短、有证据，堆客套话不加分。
3. **监控偏差。** 像 `dt-judge-bias`、`dt-length-hack-data` 里那样，检查回答长度、judge 对同家族模型的偏好，以及和人评的一致性 kappa。
4. **挑题。** 用人评检查和 cohesion 选 prompt。AFM 中有 20-30% 的题存在人评分歧，这些不适合直接交给 RLAIF。能明确验证的任务用规则奖励，AFM 2025 报告公开的做法也是人偏好训奖励模型（RM）再加规则奖励。

## 追问

- **把原则写进系统提示算不算数据？** 那只是推理时的约束。训练数据仍要示范怎样遵守这些原则，光靠约束解码管不了内容。
- **和 Self-Rewarding 有什么区别？** 宪法至少有外置的原则；Self-Rewarding 连原则也是模型自己写的，见 `dt-self-improve`。
