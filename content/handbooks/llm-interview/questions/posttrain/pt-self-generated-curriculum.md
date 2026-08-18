---
id: pt-self-generated-curriculum
section: posttrain
order: 34
level: S
title: 没有人工题库时，如何让模型自己出题、自己验证并持续提高，而不滑向 trivial task 或奖励作弊？
quick: 把题目生成、求解和验证角色分离，用学习进展而非单纯高 reward 选题；题目必须经独立可执行 verifier 和去重过滤，并保留冻结的外部评测集，防止系统只学会生成自己容易验证的题。
tags:
  - Curriculum
  - Self-play
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Absolute Zero
    url: https://arxiv.org/abs/2505.03335
    type: primary
---

自生成 curriculum 不是让同一模型随意自问自答。候选题需满足可执行性、难度区间、新颖性和 non-leakage；solver 的成功变化或 verifier 分歧可作为 learning-progress 信号，避免始终选择最简单、最容易得分的题。

出题器、求解器、verifier 最好使用隔离的版本或角色，并记录题目生成链。需要做语义去重、难度校准、对抗 prompt 检查，并限制题目直接引用答案或利用 verifier 漏洞。

最终只信独立 held-out suite。若 self-play 指标持续上升而外部成功率不动，优先怀疑 task generator 与 reward 的共适应，而不是宣称模型获得了新能力。
