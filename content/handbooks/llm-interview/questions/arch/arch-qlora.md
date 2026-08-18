---
id: arch-qlora
section: arch
order: 12
level: A
title: QLoRA 的 NF4、Double Quantization、Paged Optimizer 是什么？
quick: >-
  QLoRA 以 4-bit NF4 保存冻结 base weights，只训练 LoRA；NF4 针对近似正态权重设计量化 levels，Double
  Quantization 再压量化常数，Paged Optimizer 缓解显存峰值。
tags:
  - QLoRA
  - Quantization
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources:
  - title: ↗ QLoRA
    url: 'https://arxiv.org/abs/2305.14314'
    type: legacy-reference
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>QLoRA 以 4-bit NF4 保存冻结 base weights，只训练 LoRA；NF4 针对近似正态权重设计量化 levels，Double Quantization 再压量化常数，Paged Optimizer 缓解显存峰值。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>核心节省来自 base model 4-bit storage + 不为 full base 保存 trainable optimizer states。Forward 通常仍需要把 quantized weights 解码/参与更高精度计算，因此不是“整个训练都是 INT4 arithmetic”。</p><p>NF4 让离散 levels 更匹配 normal-like weight distribution；Double Quantization 再量化 scale/zero 等 quantization constants；Paged Optimizer 利用统一内存/分页机制处理 activation/optimizer 峰值。</p></div>
          
          
          <div class="sources"><div class="mini-title">原始材料</div><a href="https://arxiv.org/abs/2305.14314" target="_blank" rel="noopener noreferrer">↗ QLoRA</a></div>
