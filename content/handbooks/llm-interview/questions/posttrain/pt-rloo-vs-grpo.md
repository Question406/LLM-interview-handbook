---
id: pt-rloo-vs-grpo
section: posttrain
order: 25
level: A
title: RLOO 和 GRPO 都不用 Critic，它们的 baseline 有什么关键区别？
quick: >-
  两者都用同 prompt 的多条 rollout 降方差。RLOO 给每条样本用“其余样本 reward 的均值”作 leave-one-out
  baseline；GRPO 常用组均值并再按组标准差归一化，后者会改变 advantage 的尺度与统计性质。
tags:
  - RLOO
  - GRPO
  - RL
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: DeepSeekMath / GRPO
    url: 'https://arxiv.org/abs/2402.03300'
    type: legacy-reference
  - title: GRPO calibration analysis
    url: 'https://arxiv.org/abs/2508.11800'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>两者的共同点是：不训练 learned value model，而是让同 prompt 的多次采样彼此充当 baseline。差别在 baseline 是否包含当前样本、以及是否再做 group-std normalization。</p><ul><li><b>RLOO：</b>对第 i 条 rollout，用其余 G−1 条 reward 的平均值作 baseline。这样当前 reward 不会“抵消自己”，是 REINFORCE baseline 的直接构造。</li><li><b>GRPO：</b>通常先用组均值中心化，再在实现中按组标准差缩放。它适合可验证、组内有明确相对好坏的任务，但全对/全错会没有相对信号。</li><li><b>追问点：</b>标准差归一化不是纯数值技巧；它会改变不同题目的权重，对随机结果上的 calibration 也可能有影响。要说明具体实现，而不是把所有“无 critic RL”混为一谈。</li></ul><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://arxiv.org/abs/2402.03300" target="_blank" rel="noreferrer">DeepSeekMath / GRPO</a><a href="https://arxiv.org/abs/2508.11800" target="_blank" rel="noreferrer">GRPO calibration analysis</a></div></div>
