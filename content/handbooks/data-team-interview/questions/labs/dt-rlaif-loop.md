---
id: dt-rlaif-loop
section: labs
order: 9
level: A
title: Anthropic：RLAIF / 宪法反馈，judge 开始喜欢自己的文风怎么办？
quick: "固定 judge 的版本，再用人评和规则独立检查结果。策略会越来越会模仿 judge 偏爱的长文和套话，judge 要是每轮换成当前策略，就等于让模型给自己打分，最后 judge 给高分、人评却不涨。能直接验证的任务优先用规则奖励，人评分歧明显的题留给人来判断。"
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

先把 judge 的版本固定住，不随策略模型一起更新，再用人评和规则独立检查结果。judge 能在合适的任务上省掉人工标注，最后把关还是靠人和规则。

比如某一轮 judge 给「先复述问题、再分三点、最后加一段总结」的回答打分偏高，下一轮策略就会把这种写法用得更多，judge 分涨了，人读起来却更啰嗦。循环跑下去，策略越来越会模仿 judge 喜欢的长文和套话，人评没有进步，甚至下降。要是 judge 每轮还换成当前策略，就等于让模型给自己打分。

所以除了固定 judge 版本，评价原则也要写清楚：回答要简短、有证据，堆客套话不加分。训练中盯住几样偏差，包括回答长度、judge 对同家族模型的偏好，以及和人评的一致性 kappa，做法和 `dt-judge-bias`、`dt-length-hack-data` 里一样。挑题时用人评检查和 cohesion 选 prompt，能明确验证的任务直接用规则奖励。

## 追问

**RLAIF 效果真的能接近 RLHF 吗？**
对比论文报过两者效果接近，但标签可不可靠仍要单独验证。Constitutional AI 的流程是先按原则让模型批评并改写，再让模型按原则标偏好，它减少的是人工标注量。

**哪些题不适合交给 RLAIF？**
人评本身就有明显分歧的题。AFM 中有 20-30% 的题存在人评分歧，这些不适合直接交给 AI judge。AFM 2025 报告公开的做法也是用人偏好训奖励模型（RM），再加规则奖励。

**把原则写进系统提示算不算数据？**
不算，那只是推理时的约束。训练数据仍要示范怎样遵守这些原则，光靠约束解码管不了内容。

**和 Self-Rewarding 有什么区别？**
宪法至少有外置的原则；Self-Rewarding 连原则也是模型自己写的，见 `dt-self-improve`。
