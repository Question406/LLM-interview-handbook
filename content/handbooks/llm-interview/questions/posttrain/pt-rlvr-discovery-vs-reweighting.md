---
id: pt-rlvr-discovery-vs-reweighting
section: posttrain
order: 39
level: S
title: 如何实验区分 RLVR 学到了新推理路径，还是只把 base model 原有正确路径重加权？
quick: 先在 base model 上用大 K 测正确路径覆盖，再比较 RL 后路径是否已被 base rollout 包含；联合看 Pass@1 / Pass@K、路径相似度和跨分布泛化。只见 Pass@1 涨不能证明发现了新算法。
tags:
  - RLVR
  - Exploration
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: https://arxiv.org/abs/2504.13837
    type: primary
---

先为每题收集 base policy 的高 K rollout，建立它本来能触及的正确答案和过程模式集合。再看 RL policy 的成功轨迹是否落在此集合或近邻中；若大量新成功只是在原集合中更常被采样，主要是 reweighting。

要控制 prompt、temperature、token budget 和 verifier；比较 answer-level 与 trace-level containment。还需在与训练 reward 不同的分布上评估，因为真实 discovery 应更可能带来结构性泛化，而不是仅适配原任务。

这个实验并非否定 reweighting 的价值。把稀有正确策略变成 Pass@1 可用能力本身很有价值，只是不能误称为“从零创造新 reasoning”。
