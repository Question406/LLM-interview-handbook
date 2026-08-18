---
id: sys-precision
section: systems
order: 4
level: A
title: BF16 vs FP16 vs FP8：训练时怎么理解？
quick: >-
  BF16 与 FP32 都有 8-bit exponent，动态范围大，训练更不易 overflow；FP16 mantissa 更多但 exponent
  小，常需 loss scaling；FP8 进一步省带宽/算力，但需要 scale management、格式选择与敏感层高精度保留。
tags:
  - Precision
  - Training
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>BF16 与 FP32 都有 8-bit exponent，动态范围大，训练更不易 overflow；FP16 mantissa 更多但 exponent 小，常需 loss scaling；FP8 进一步省带宽/算力，但需要 scale management、格式选择与敏感层高精度保留。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>FP16：5 exponent / 10 fraction（不含 hidden bit）；BF16：8 exponent / 7 fraction。BF16 范围接近 FP32，因此大模型训练常更稳。</p><p>FP8 常有 E4M3/E5M2 等格式：一个更精确、一个范围更大。训练需要 per-tensor/per-channel scale、amax history、stochastic rounding/高精累加等策略；并非所有 op 都适合 FP8。</p></div>
