---
id: arch-mtp
section: arch
order: 19
level: A
title: Multi-Token Prediction（MTP）训练目标能带来什么？为什么不等于“每次 decode 多吐几个 token”？
quick: >-
  MTP 让模型在训练时预测多个未来 token，可增强序列表征；若把额外头作为 speculative draft，还需要 target
  verification 和足够 acceptance rate，才能在不改变目标分布的前提下获得实际加速。
tags:
  - MTP
  - Speculative Decoding
  - Architecture
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: DeepSeek-V3 / MTP
    url: 'https://arxiv.org/abs/2412.19437'
    type: legacy-reference
  - title: FlashAttention
    url: 'https://arxiv.org/abs/2205.14135'
    type: legacy-reference
---
<div class="full-answer"><div class="mini-title">完整答案</div><p>标准 next-token loss 只直接监督 t+1。MTP 增加多个未来位置的预测目标，让 hidden state 被要求携带更长程的可预测信息；其价值首先是训练信号，不是魔法式地改变 autoregressive 语义。</p><ul><li><b>训练：</b>定义每个预测头对应的 offset、loss 权重与 teacher forcing 边界，避免 future label 泄漏到主干输入。</li><li><b>推理：</b>draft 一次提出多个 token，target model 并行验证；被拒绝部分仍按 target 修正，因此目标分布由验证规则保证。</li><li><b>系统收益：</b>取决于 draft 成本、acceptance rate、KV/调度开销。若候选质量差，反而只增加工作量。</li></ul><div class="sources"><div class="mini-title">延伸阅读</div><a href="https://arxiv.org/abs/2412.19437" target="_blank" rel="noreferrer">DeepSeek-V3 / MTP</a><a href="https://arxiv.org/abs/2205.14135" target="_blank" rel="noreferrer">FlashAttention</a></div></div>
