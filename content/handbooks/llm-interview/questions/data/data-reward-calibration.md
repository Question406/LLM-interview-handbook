---
id: data-reward-calibration
section: data
order: 14
level: S
title: Reward Model / Judge 的 rank accuracy 高，为什么还要看 calibration？
quick: >-
  排序对不等于分数可信。accuracy 只问“谁更高”，calibration 还问“0.9 的置信度是否真的约有 90%
  正确”；一旦分数被用于阈值、拒答、采样或 RL，错误尺度会直接改变决策。
tags:
  - Reward Model
  - Calibration
  - Eval
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: RewardBench
    url: 'https://arxiv.org/abs/2403.13787'
    type: legacy-reference
  - title: Calibration paper
    url: 'https://arxiv.org/abs/1706.04599'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>如果 judge 只用于每对二选一，排序正确率很重要；但工程里它常被用于筛选阈值、best-of-N、数据权重或作为 RL reward。此时分数尺度错误会造成过度过滤、过度优化或风险判断失真。</p><ul><li><b>看 reliability：</b>按预测置信度分桶，比较预测概率与真实偏好频率；同时报告 Brier / log loss，而非只报 accuracy。</li><li><b>看 OOD：</b>按长度、语言、领域、格式、对抗样本和 policy 版本切片；高分回答要抽样人工审计。</li><li><b>再决定用途：</b>可用 temperature / isotonic 等做后校准，但校准集必须独立；若 reward 只在训练分布可靠，就不应把它当无边界的 RL oracle。</li></ul><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://arxiv.org/abs/2403.13787" target="_blank" rel="noreferrer">RewardBench</a><a href="https://arxiv.org/abs/1706.04599" target="_blank" rel="noreferrer">Calibration paper</a></div></div>
